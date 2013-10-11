from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    '''
    URLconf handler for the addressbook
    '''
    page_title = "Addressbook"
    
    # add a list of pages in the view
    globals['sections'] = getSiteSections('addressbook')
    
    context = {'globals': globals, 'page_title': page_title}
    return render(request, 'addressbook/index.html', context)
