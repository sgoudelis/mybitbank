from django import template

def keyvalue(value, arg):
    try:
        return value[arg]
    except:
        return False

register = template.Library()
register.filter('keyvalue', keyvalue)
