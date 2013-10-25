import config
import generic
import forms
from connections import connector
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

current_section = 'login'

def index(request):
    '''
    Login form
    '''
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard:index'))
        
    page_title = _("Login")
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, 'all'), 
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
            print login_form.cleaned_data
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            remember = login_form.cleaned_data['remember']
            next_url = login_form.cleaned_data['next_url']
            print "remember: %s" % remember
            # try to authenticate user
            user = authenticate(username=username, password=password)
        
            if user is not None and user.is_active:
                # authenticated, log user in
                login(request, user)
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
    
        else:
            # form not valid so auth failed
            auth_process = False
            auth_message = ""
            
    # check 
    if not auth_process:
        page_title = _("Login")
        context = {
                   'globals': config.MainConfig['globals'], 
                   'breadcrumbs': generic.buildBreadcrumbs(current_section, 'all'), 
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
    logout(request)

    return HttpResponseRedirect(reverse('login:index'))