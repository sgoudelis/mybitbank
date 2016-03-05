"""
The MIT License (MIT)

Copyright (c) 2016 Stratos Goudelis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import calendar
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.timezone import utc
from django.utils.translation import ugettext as _

import forms
from models import savedAddress
from mybitbank.libs import events, misc
from mybitbank.libs.config import MainConfig
from mybitbank.libs.connections import connector


current_section = 'addressbook'

@login_required
def index(request):
    '''
    URLconf handler for the addressbook
    '''
    
    context = getAddressBookCommonContext(request=request)
    return render(request, 'addressbook/index.html', context)

def getAddressBookCommonContext(request, form=None):
    '''
    Get common context
    '''
    page_title = "Addressbook"
    
    # add a list of pages in the view
    sections = misc.getSiteSections('addressbook')
    currency_symbols = misc.getCurrencySymbol(connector)
    book = savedAddress.objects.filter(status__gt=0)
    currencies_available = []
    for provider_id in connector.services.keys():
        currencies_available.append({'provider_id': provider_id, 'currency': connector.config[provider_id]['currency'], 'name': connector.config[provider_id]['name']})
        
    for address in book:
        timestamp = calendar.timegm(address.entered.timetuple())
        address.time_pretty = misc.twitterizeDate(timestamp)
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
               'globals': MainConfig['globals'],
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'user': request.user,
               'breadcrumbs': misc.buildBreadcrumbs(current_section),
               'page_sections': sections,
               'page_title': page_title,
               'book': book,
               'currencies': currencies_available,
               'currency_symbols': currency_symbols,
               'form': form,
               }
    
    return context

def add(request):
    '''
    
    '''
    form = forms.AddAddressBookForm()
    context = getAddressBookCommonContext(request=request, form=form)
    context['breadcrumbs'] = misc.buildBreadcrumbs(current_section, '', 'Add address')
    return render(request, 'addressbook/add.html', context)
    
def create(request):
    '''
    Create a new address book entry
    '''
    
    # set the request in the connector object
    connector.request = request
    
    if request.method == 'POST': 
        # we have a POST request
        form = forms.AddAddressBookForm(request.POST)
        
        if form.is_valid():
            # form is valid
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            provider_id = form.cleaned_data['provider_id']
            comment = form.cleaned_data['comment']
            
            # add address to addressbook
            newAddressEntry = savedAddress(name=name, address=address, currency=connector.config[provider_id]['currency'], comment=comment, status=2, entered=datetime.datetime.utcnow().replace(tzinfo=utc))
            newAddressEntry.save()
            messages.success(request, 'Addressbook entry added for %s with address %s' % (name, address), extra_tags="success")
            events.addEvent(request, 'Addressbook entry added for %s with name "%s"' % (address, name), 'info')
            
            return HttpResponseRedirect(reverse('addressbook:index'))
        else:
            # form not valid
            pass
            
    else:
        # not a POST
        form = forms.AddAddressBookForm()
    
    context = getAddressBookCommonContext(request=request, form=form)
    context['breaddrumbs'] = misc.buildBreadcrumbs(current_section, '', 'Add address')
    return render(request, 'addressbook/add.html', context)
                
                
def delete(request, addressid):
    '''
    Set status to 0
    '''
    addressbook = savedAddress.objects.filter(id=addressid)
    
    if addressbook:
        name = addressbook[0].name
        address = addressbook[0].address
        addressbook[0].status = 0
        addressbook[0].save()
        messages.success(request, 'Addressbook entry %s with address %s deleted' % (name, address), extra_tags="warning")
        events.addEvent(request, 'Addressbook entry deleted with name "%s" and address "%s"' % (name, address), 'warning')
        
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
            addressbook[0].status = 2
            addressbook[0].save()
            messages.success(request, 'Addressbook entry %s with address %s enabled' % (name, address), extra_tags="info")
            events.addEvent(request, 'Addressbook entry enabled with name "%s" and address "%s"' % (name, address), 'info')
        else:
            addressbook[0].status = 1
            addressbook[0].save()
            messages.success(request, 'Addressbook entry %s with address %s disabled.' % (name, address), extra_tags="warning")
            events.addEvent(request, 'Addressbook entry disabled with name "%s" and address "%s"' % (name, address), 'warning')
            
    return HttpResponseRedirect(reverse('addressbook:index'))
    
