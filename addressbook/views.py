import config
import generic
import forms
import datetime
from connections import connector
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from models import savedAddress

current_section = 'addressbook'

@login_required
def index(request):
    '''
    URLconf handler for the addressbook
    '''
    
    context = getAddressBookCommonContext(request=request)
    
    return render(request, 'addressbook/index.html', context)

def getAddressBookCommonContext(request, form=None):
    
    page_title = "Addressbook"
    
    # add a list of pages in the view
    sections = generic.getSiteSections('addressbook')
    currency_symbols = generic.getCurrencySymbol()
    book = savedAddress.objects.filter(status__gt=0)
    currencies_available = []
    currencies = connector.services.keys()
    for curr in currencies:
        currencies_available.append({'name': curr, 'title': connector.config[curr]['currency_name']})
        
    context = {
               'globals': config.MainConfig['globals'], 
               'user': request.user,
               'breadcrumbs': generic.buildBreadcrumbs(current_section), 
               'page_sections': sections, 
               'page_title': page_title,
               'book': book,
               'currencies': currencies_available, 
               'currency_symbols': currency_symbols,
               'form': form,
               }
    
    return context

def add(request):
    
    form = forms.AddAddressBookForm()
    context = getAddressBookCommonContext(request=request,form=form)
    context['breadcrumbs'] = generic.buildBreadcrumbs(current_section, '', 'Add address')
    return render(request, 'addressbook/add.html', context)
    
def create(request):
    if request.method == 'POST': 
        # we have a POST request
        form = forms.AddAddressBookForm(request.POST)
        
        if form.is_valid():
            # form is valid
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            currency = form.cleaned_data['currency']
            comment =  form.cleaned_data['comment']
            
            # add address to addressbook
            newAddressEntry = savedAddress(name=name, address=address, currency=currency, comment=comment, status=2, entered=datetime.datetime.now())
            newAddressEntry.save()
            return HttpResponseRedirect(reverse('addressbook:index'))
        else:
            # form not valid
            pass
            
    else:
        # not a POST
        form = forms.AddAddressBookForm()
    
    context = getAddressBookCommonContext(request=request, form=form)
    context['breaddrumbs'] = generic.buildBreadcrumbs(current_section, '', 'Add address')
    return render(request, 'addressbook/add.html', context)
                
                
def delete(request, addressid):
    
    
    addressbook = savedAddress.objects.filter(id=addressid)
    
    if addressbook:
        addressbook[0].status=0
        addressbook[0].save()
        
    return HttpResponseRedirect(reverse('addressbook:index'))
    
