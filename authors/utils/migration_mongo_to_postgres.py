from pymongo import MongoClient
import django
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "authors.settings")
django.setup()

client = MongoClient("mongodb://localhost")

db = client.local

authors = db.authors.find()

from quotes.models import Author, Quote, Tag

for author in authors:
    Author.objects.get_or_create(
        fullname=author['fullname'],
        born_date=author['born_date'],
        born_location=author['born_location'],
        description=author['description']
    )

quotes = db.quotes.find()

for quote in quotes:
    tags = []
    for tag in quote['tags']:
        t, created = Tag.objects.get_or_create(name=tag)
        if created:
            print(f"Created new Tag: {t.name}")
        else:
            print(f"Using existing Tag: {t.name}")
        tags.append(t)
    exist_quote = Quote.objects.filter(quote=quote['quote'])

    if not exist_quote:
        author = db.authors.find_one({'_id': quote['author']})
        a = Author.objects.get(fullname=author['fullname'])
        q = Quote.objects.create(
            quote=quote['quote'],
            author=a
        )
        q.save()
        for tag in tags:
            q.tags.add(tag)