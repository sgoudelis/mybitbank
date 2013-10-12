from django import template

def keyvalue(value, arg):
    return value[arg]

register = template.Library()
register.filter('keyvalue', keyvalue)
