# -*- coding=utf-8 -*-
"""
User login and logout views.
"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mspray.apps.main import ona

FORM_ID = getattr(settings, 'ONA_FORM_PK', None)


def get_form_owners(formid):
    """
    Returns a list of usernames of users with the role 'owner' in the Ona Form.
    """
    form = ona.fetch_form(formid)
    owners = []
    role = 'owner'
    if form:
        users = form.get('users')
        if users:
            owners = [user['user'] for user in users if user['role'] == role]
    return owners


def login(request):
    """
    User login view.
    """
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username1')
        password = request.POST.get('password1')
        if username and password:
            auth = ona.login(username, password)
            if auth:
                owners = get_form_owners(FORM_ID)
                if username in owners:
                    request.session['show_csv'] = True

                    return HttpResponseRedirect('/')
            context = {
                'error': "Wrong username or password. Please try again."
            }
    else:
        if settings.DEBUG:
            request.session['show_csv'] = True
        if request.session.get('show_csv'):
            return HttpResponseRedirect('/')

    return render(request, 'home/login.html', context)


def logout(request):
    """
    Logout user, clears all sessions, redirect to /.
    """
    request.session.flush()

    return HttpResponseRedirect('/')
