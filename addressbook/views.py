import config
import generic
import forms
import datetime
import calendar
from connections import connector
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.utils.timezone import utc
from models import savedAddress
from django.contrib import messages

current_section = 'addressbook'

@login_required
def index(request):
    '''
    URLconf handler for the addressbook
    '''
    
    context = getAddressBookCommonContext(request=request)
    print connector.errors
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
        
    for address in book:
        timestamp = calendar.timegm(address.entered.timetuple())
        address.time_pretty = generic.twitterizeDate(timestamp)
        if address.status == 1:
            address.button_text = _("enable")
            address.status_text = 'Hidden'
            address.icon = "glyphicon-minus-sign"
            address.icon_color = 'red-font'
        elif address.status == 2:
            address.button_text = _("disable")
            address.status_text = 'Active'
            address.icon = "glyphicon-ok-circle"
            address.icon_color = 'green-font'
    
    context = {
               'globals': config.MainConfig['globals'], 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
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
            newAddressEntry = savedAddress(name=name, address=address, currency=currency, comment=comment, status=2, entered=datetime.datetime.utcnow().replace(tzinfo=utc))
            newAddressEntry.save()
            messages.success(request, 'Addressbook entry added for %s with address %s' % (name, address), extra_tags="success")
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
    '''
    Set status to 0
    '''
    addressbook = savedAddress.objects.filter(id=addressid)
    
    if addressbook:
        name = addressbook[0].name
        address = addressbook[0].address
        addressbook[0].status=0
        addressbook[0].save()
        messages.success(request, 'Addressbook entry %s with address %s deleted' % (name, address), extra_tags="warning")
    
    return HttpResponseRedirect(reverse('addressbook:index'))
    
def toggleStatus(request, addressid):
    '''
    Toggle status
    '''
    addressbook = savedAddress.objects.filter(id=addressid)
    
    if len(addressbook):
        name = addressbook[0].name
        address = addressbook[0].address
        if addressbook[0].status == 1:
            addressbook[0].status=2
            addressbook[0].save()
            messages.success(request, 'Addressbook entry %s with address %s enabled' % (name, address), extra_tags="info")
        else:
            addressbook[0].status=1
            addressbook[0].save()
            messages.success(request, 'Addressbook entry %s with address %s disabled.' % (name, address), extra_tags="warning")
            
    return HttpResponseRedirect(reverse('addressbook:index'))
    
