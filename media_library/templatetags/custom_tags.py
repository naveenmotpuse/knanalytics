from django import template

register = template.Library()

@register.filter
def index(sequence, position):
    return position+1

@register.filter
def list_index(resultslist, position):
    return position == 0

@register.simple_tag
def define(the_string):
    return the_string
