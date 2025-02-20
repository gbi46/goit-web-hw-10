from django.db import models
from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField
from mongoengine import BooleanField, CASCADE, EmailField, StringField

class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = DateTimeField(max_length=50)
    born_location = StringField(max_length=150)
    description = StringField()
    meta = {"collection": "authors"}

class Quote(Document):
    tags = ListField(StringField(max_length=15))
    author = ReferenceField(Author, required=True, reverse_delete_rule=CASCADE)
    quote = StringField()
    meta = {"collection": "quotes"}

