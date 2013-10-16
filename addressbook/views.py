import config
import generic
from django.shortcuts import render

current_section = 'addressbook'

def index(request):
    '''
    URLconf handler for the addressbook
    '''
    page_title = "Addressbook"
    
    # add a list of pages in the view
    sections = generic.getSiteSections('addressbook')
    
    context = {'globals': config.MainConfig['globals'], 'breadcrumbs': generic.buildBreadcrumbs(current_section), 'page_sections': sections, 'page_title': page_title}
    return render(request, 'addressbook/index.html', context)
