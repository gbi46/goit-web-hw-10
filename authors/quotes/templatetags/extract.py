from bson.objectid import ObjectId
from django import template
from ..models import Author
from ..utils import create_mongodb_connection

register = template.Library()
create_mongodb_connection()

def get_author(quote):
    if hasattr(quote, 'author') and quote.author:
        return quote.author.fullname
    else:
        return 'no author'

register.filter('author', get_author)

def get_author_id(quote):
    if hasattr(quote, 'author') and quote.author:
        return quote.author.id
    else:
        return 'no author'

register.filter('author_id', get_author_id)

def get_tag_font_size(value):
    try:
        return 20 - value
    except (ValueError, TypeError):
        return 0

register.filter('tag_font_size', get_tag_font_size)
