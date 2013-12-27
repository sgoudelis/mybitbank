import socket

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

import forms
from mybitbank.libs import events, misc
from mybitbank.libs.config import MainConfig
from mybitbank.libs.connections import connector


current_section = 'login'

def index(request):
    '''
    Login form
    '''
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard:index'))
        
    page_title = _("Login")
    context = {
               'globals': MainConfig['globals'], 
               'breadcrumbs': misc.buildBreadcrumbs(current_section, 'all'), 
               'system_errors': connector.errors,
               'page_title': page_title, 
               'next_url': request.GET.get('next', reverse('dashboard:index')),
               }
    return render(request, 'login/index.html', context)

def processLogin(request): 
    '''
    Authenticate user
    '''
    
    auth_process = False
    
    if request.method == 'POST': 
        # we have a POST request
        login_form = forms.LoginForm(request.POST)
        
        if login_form.is_valid():
            # all validation rules pass
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            remember = login_form.cleaned_data['remember']
            next_url = login_form.cleaned_data['next_url']

            # try to authenticate user
            user = authenticate(username=username, password=password)
            client_ip = misc.getClientIp(request)
            
            try:
                client_hostname_tuple = socket.gethostbyaddr(client_ip)
            except:
                client_hostname_tuple = ()
                
            if client_hostname_tuple:
                client_hostname = client_hostname_tuple[0]
            else:
                client_hostname = 'n/a'
        
            if user is not None and user.is_active:
                # authenticated, log user in
                login(request, user)
                events.addEvent(request, 'Login occurred from %s (%s)' % (client_hostname, client_ip), 'info')
                
                if remember:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(300)
                    
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return HttpResponseRedirect(reverse('dashboard:index'))
            else:
                # failed to authenticate password
                auth_process = False
                auth_message = "Username and password combination incorrect"
                events.addEvent(username, 'Login failed from %s (%s) username: %s' % (client_hostname, client_ip, username), 'alert')
        else:
            # form not valid so auth failed
            auth_process = False
            auth_message = ""
    else:
        auth_process = False
        auth_message = ""
        login_form = forms.LoginForm()
            
    # check 
    if not auth_process:
        page_title = _("Login")
        context = {
                   'globals': MainConfig['globals'], 
                   'breadcrumbs': misc.buildBreadcrumbs(current_section, 'all'), 
                   'system_errors': connector.errors,
                   'page_title': page_title, 
                   'form': login_form,
                   'main_error': auth_message,
                   }
        
    return render(request, 'login/index.html', context)

@login_required
def processLogout(request):
    '''
    Logout
    '''
    
    events.addEvent(request, 'Logout occurred', 'info')
    logout(request)
    
    return HttpResponseRedirect(reverse('login:index'))