import os
import sys

from fabric.api import env, run, cd, lcd, sudo, put, prefix
from fabric.contrib import files


DEPLOYMENTS = {
    'default': {
        'home': '/home/ubuntu/src',
        'host_string':
        'ubuntu@107.20.178.211',
        'project': 'mspray',
        'key_filename': os.path.expanduser('~/.ssh/ona.pem'),
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


def setup_env(deployment_name):
    env.update(DEPLOYMENTS[deployment_name])

    if not check_key_filename(deployment_name):
        sys.exit(1)

    env.code_src = os.path.join(env.home, env.project)
    env.virtualenv = os.path.join(env.home, '.virtualenvs')


def change_local_settings(config_module, dbname, dbuser, dbpass,
                          dbhost='127.0.0.1',
                          deployment_name='default'):
    setup_env(deployment_name)
    lconfig_path = os.path.join('mspray',
                                'preset', 'local_settings.py')
    config_path = os.path.join(env.code_src, lconfig_path)
    with cd(env.code_src):
            run('mkdir -p mspray/preset')
    put(os.path.join('context', lconfig_path), config_path)
    if files.exists(config_path):
        files.sed(config_path, 'REPLACE_DB_NAME', dbname)
        files.sed(config_path, 'REPLACE_DB_USER', dbuser)
        files.sed(config_path, 'REPLACE_DB_PASSWORD', dbpass)
        files.sed(config_path, 'REPLACE_DB_HOST', dbhost)


def system_setup(deployment_name, dbuser='dbuser', dbpass="dbpwd"):
    setup_env(deployment_name)
    sudo('sh -c \'echo "deb http://apt.postgresql.org/pub/repos/apt/ '
         'precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list\'')
    sudo('wget --quiet -O - http://apt.postgresql.org/pub'
         '/repos/apt/ACCC4CF8.asc | apt-key add -')
    sudo('apt-get update')
    sudo('apt-get install -y nginx git python3 python3-setuptools'
         ' python3-dev binutils'
         ' libproj-dev gdal-bin Postgresql-9.3 libpq-dev')
    sudo('easy_install3 pip')
    sudo('pip3 install virtualenvwrapper uwsgi')
    run('sudo -u postgres psql -U postgres -d postgres'
        ' -c "CREATE USER %s with password \'%s\';"' % (dbuser, dbpass))
    run('sudo -u postgres psql -U postgres -d postgres'
        ' -c "CREATE DATABASE %s OWNER %s;"' % (dbuser, dbuser))
    run('sudo -u postgres psql -U postgres -d %s'
        ' -c "CREATE EXTENSION POSTGIS;"' % (dbuser))


def server_setup(deployment_name, dbuser='dbuser', dbpass="dbpwd"):
    setup_env(deployment_name)

    sudo('mkdir -p %s' % env.home)
    sudo('chown -R ubuntu %s' % env.home)

    with cd(env.home):
        run('git clone git@github.com:onaio/mspray.git mspray'
            ' || (cd mspray && git fetch && git checkout origin/master)')

    with lcd(current_working_dir):
        change_local_settings(env.django_module, dbuser, dbuser, dbpass)

        put('context/etc/nginx/sites-available/nginx.conf',
            '/etc/nginx/conf.d/mspray.conf', use_sudo=True)
        put('context/etc/supervisor/conf.d/mspray.conf',
            '/etc/supervisor/conf.d/mspray.conf', use_sudo=True)
    data = {
        'venv': env.virtualenv, 'project': env.project
    }
    with prefix('WORKON_HOME=%(venv)s' % data):
        run('source `which virtualenvwrapper.sh`'
            ' && WORKON_HOME=%(venv)s mkvirtualenv -p  `which python3`'
            ' %(project)s' % data)

        with cd(env.code_src):
            run_in_virtualenv('pip3 install -r requirements.pip')
            run_in_virtualenv("python3 manage.py syncdb --noinput"
                              " --settings='%s'" % env.django_module)
            run_in_virtualenv("python3 manage.py migrate --settings='%s'"
                              % env.django_module)
            run_in_virtualenv("python3 manage.py collectstatic --noinput"
                              " --settings='%s'" % env.django_module)

    sudo('/etc/init.d/nginx restart')
    sudo('mkdir -p /var/log/uwsgi')
    sudo('chown -R ubuntu /var/log/uwsgi')
    sudo('mkdir -p /var/log/mspray')
    sudo('supervisorctl reload')


def deploy(deployment_name, dbuser='dbuser', dbpass="dbpwd"):
    setup_env(deployment_name)

    with cd(env.home):
        run('cd mspray && git fetch && git checkout origin/master')

    data = {
        'venv': env.virtualenv, 'project': env.project
    }
    with prefix('WORKON_HOME=%(venv)s' % data):
        run('source `which virtualenvwrapper.sh`'
            ' && WORKON_HOME=%(venv)s workon %(project)s' % data)

        with cd(env.code_src):
            run_in_virtualenv('pip3 install -r requirements.pip --upgrade')
            run_in_virtualenv("python3 manage.py syncdb --noinput"
                              " --settings='%s'" % env.django_module)
            run_in_virtualenv("python3 manage.py migrate --settings='%s'"
                              % env.django_module)
            run_in_virtualenv("python3 manage.py collectstatic --noinput"
                              " --settings='%s'" % env.django_module)

    sudo('/etc/init.d/nginx reload')
    sudo('supervisorctl reload')
