import os
import sys

from fabric.api import env, run, cd, lcd, sudo, put, prefix
from fabric.contrib import files


DEPLOYMENTS = {
    'default': {
        'home': '/home/ubuntu/src',
        'host_string':
        'ubuntu@52.28.222.219',
        'key_filename': '/home/ukanga/.ssh/ona.pem',
        'django_module': 'mspray.preset.local_settings'
    },
}

current_working_dir = os.path.dirname(__file__)


def run_in_virtualenv(command):
    d = {
        'activate': os.path.join(
            env.virtualenv, env.project, 'bin', 'activate'),
        'command': command,
    }
    run('source %(activate)s && %(command)s' % d)


def check_key_filename(deployment_name):
    if 'key_filename' in DEPLOYMENTS[deployment_name] and \
       not os.path.exists(DEPLOYMENTS[deployment_name]['key_filename']):
        print("Cannot find required permissions file: %s" %
              DEPLOYMENTS[deployment_name]['key_filename'])

        return False

    return True


def setup_env(deployment_name, project='mspray-project'):
    env.update(DEPLOYMENTS[deployment_name])

    if not check_key_filename(deployment_name):
        sys.exit(1)
    env.project = project
    env.code_src = os.path.join(env.home, env.project)
    env.virtualenv = os.path.join(env.home, '.virtualenvs')


def change_local_settings(config_module, dbname, dbuser, dbpass,
                          dbhost='127.0.0.1',
                          deployment_name='default', project='mspray-project'):
    setup_env(deployment_name, project)
    lconfig_path = os.path.join('context', 'mspray', 'preset', project,
                                'local_settings.py')
    if not os.path.exists(lconfig_path):
        lconfig_path = os.path.join('context', 'mspray', 'preset',
                                    'local_settings.py')
    config_path = os.path.join(env.code_src, 'mspray', 'preset',
                               'local_settings.py')

    with cd(env.code_src):
            run('mkdir -p mspray/preset')
    put(lconfig_path, config_path)
    if files.exists(config_path):
        files.sed(config_path, 'REPLACE_DB_NAME', dbname)
        files.sed(config_path, 'REPLACE_DB_USER', dbuser)
        files.sed(config_path, 'REPLACE_DB_PASSWORD', dbpass)
        files.sed(config_path, 'REPLACE_DB_HOST', dbhost)
        files.sed(config_path, 'PROJECT', env.project)


def db_create(deployment_name, dbname, dbuser, project='mspray-project'):
    setup_env(deployment_name, project)
    run('sudo -u postgres psql -U postgres -d postgres'
        ' -c "CREATE DATABASE %s OWNER %s;"' % (dbname, dbuser))
    run('sudo -u postgres psql -U postgres -d %s'
        ' -c "CREATE EXTENSION POSTGIS;"' % (dbname))
    run('sudo -u postgres psql -U postgres -d %s'
        ' -c "CREATE EXTENSION POSTGIS_TOPOLOGY;"' % (dbname))


def system_setup(deployment_name, dbuser='dbuser', dbpass="dbpwd",
                 project='mspray-project'):
    setup_env(deployment_name, project)
    sudo('sh -c \'echo "deb http://apt.postgresql.org/pub/repos/apt/ '
         'trusty-pgdg main" > /etc/apt/sources.list.d/pgdg.list\'')
    sudo('wget --quiet -O - http://apt.postgresql.org/pub'
         '/repos/apt/ACCC4CF8.asc | apt-key add -')
    sudo('apt-get update')
    sudo('apt-get install -y nginx git python3 python3-setuptools'
         ' python3-dev binutils'
         ' libproj-dev gdal-bin Postgresql-9.3 postgresql-9.3-postgis-2.1'
         ' postgresql-9.3-postgis-2.1-scripts libpq-dev supervisor')
    sudo('easy_install3 pip')
    sudo('pip3 install virtualenvwrapper uwsgi')
    run('sudo -u postgres psql -U postgres -d postgres'
        ' -c "CREATE USER %s with password \'%s\';"' % (dbuser, dbpass))
    db_create(deployment_name, dbuser, dbuser, project)


def server_setup(deployment_name, branch='master', dbuser='dbuser',
                 dbpass="dbpwd", dbname='dbuser', port='8008',
                 project='mspray-project'):
    setup_env(deployment_name, project)

    sudo('mkdir -p %s' % env.home)
    sudo('chown -R ubuntu %s' % env.home)

    with cd(env.home):
        run('git clone git@github.com:onaio/mspray.git {}'
            ' || (cd {} && git fetch)'.format(
                env.project, env.project
            ))
        run('cd {} && git checkout origin/{}'.format(env.project, branch))

    with lcd(current_working_dir):
        change_local_settings(env.django_module, dbname, dbuser, dbpass,
                              project=project)
        nginx_conf = '/etc/nginx/conf.d/%(project)s.conf' % env
        put('context/etc/nginx/sites-available/nginx.conf', nginx_conf,
            use_sudo=True)
        files.sed(nginx_conf, 'PROJECT', env.project, use_sudo=True)
        files.sed(nginx_conf, 'PORT', port, use_sudo=True)
        supervisor_conf = '/etc/supervisor/conf.d/%(project)s.conf' % env
        put('context/etc/supervisor/conf.d/mspray.conf', supervisor_conf,
            use_sudo=True)
        files.sed(supervisor_conf, 'PROJECT', env.project, use_sudo=True)
        uwsgi_path = os.path.join(
            env.code_src, 'mspray', 'preset', 'uwsgi.ini'
        )
        put('context/mspray/preset/uwsgi.ini', uwsgi_path)
        files.sed(uwsgi_path, 'PROJECT', env.project)
        files.sed(uwsgi_path, 'PORT', port)
    data = {
        'venv': env.virtualenv, 'project': env.project
    }
    with prefix('WORKON_HOME=%(venv)s '
                'VIRTUALENVWRAPPER_PYTHON=`which python3`' % data):
        run('source `which virtualenvwrapper.sh`'
            ' && WORKON_HOME=%(venv)s mkvirtualenv -p  `which python3`'
            ' %(project)s' % data)

        with cd(env.code_src):
            run_in_virtualenv('pip3 install -r requirements.pip')
            run_in_virtualenv("python3 manage.py migrate --settings='%s'"
                              % env.django_module)
            run_in_virtualenv("python3 manage.py collectstatic --noinput"
                              " --settings='%s'" % env.django_module)

    sudo('/etc/init.d/nginx restart')
    sudo('mkdir -p /var/log/uwsgi')
    sudo('chown -R ubuntu /var/log/uwsgi')
    sudo('mkdir -p /var/log/mspray')
    sudo('supervisorctl reload')


def deploy(deployment_name, branch='master', dbuser='dbuser', dbpass="dbpwd",
           dbname='dbuser', port='8008', project='mspray-project'):
    setup_env(deployment_name, project)

    with cd(env.home):
        run('cd {} && git fetch && git checkout origin/{}'
            .format(env.project, branch))

    data = {
        'venv': env.virtualenv, 'project': env.project
    }
    with prefix('WORKON_HOME=%(venv)s '
                'VIRTUALENVWRAPPER_PYTHON=`which python3`' % data):
        run('source `which virtualenvwrapper.sh`'
            ' && WORKON_HOME=%(venv)s workon %(project)s' % data)

        with cd(env.code_src):
            change_local_settings(env.django_module, dbname, dbuser, dbpass,
                                  project=project)
            run_in_virtualenv('pip3 install -r requirements.pip --upgrade')
            run_in_virtualenv("python3 manage.py migrate --settings='%s'"
                              % env.django_module)
            run_in_virtualenv("python3 manage.py collectstatic --noinput"
                              " --settings='%s'" % env.django_module)

    sudo('/etc/init.d/nginx reload')
    sudo('supervisorctl reload')


def create_buffers(deployment_name, distance=15, dbuser='dbuser',
                   dbpass="dbpwd", project='mspray-project'):
    setup_env(deployment_name, project)
    data = {
        'venv': env.virtualenv, 'project': env.project
    }
    with prefix('WORKON_HOME=%(venv)s' % data):
        run('source `which virtualenvwrapper.sh`'
            ' && WORKON_HOME=%(venv)s workon %(project)s' % data)

        with cd(env.code_src):
            run_in_virtualenv("python3 manage.py create_household_buffers"
                              " -d %s -f true --settings='%s'"
                              % (distance, env.django_module))
