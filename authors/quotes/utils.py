from .models import Author, Quote, Tag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mongoengine import connect
from pathlib import Path
from pymongo import MongoClient
from urllib.parse import quote_plus
import configparser

FILES_PATH = Path(__file__).parent

def create_mongodb_connection():

    config = configparser.ConfigParser()
    config_filename = FILES_PATH.joinpath('config.ini')
    config.read(config_filename, encoding='utf-8')

    MongoDB_USER = quote_plus(config.get('DB', 'USER'))
    MongoDB_psw = quote_plus(config.get('DB', 'PASS'))
    MongoDB_db_name = config.get('DB', 'DB_NAME')
    MongoDB_domain = config.get('DB', 'DOMAIN')

    uri = f"""mongodb+srv://{MongoDB_USER}:{MongoDB_psw}@{MongoDB_domain}/{MongoDB_db_name}?retryWrites=true&w=majority&appName=Cluster0&ssl=true"""

    connect(host=uri)

def get_data_from_mongo(page=1, per_page=10):
    client = MongoClient("mongodb://localhost:27017/")
    db = client.local

    authors = {str(author['_id']): author for author in db.authors.find()}

    total_quotes = db.quotes.count_documents({})
    print(total_quotes)
    skip = (page - 1) * per_page
    quotes_cursor = db.quotes.find().skip(skip).limit(per_page)

    quotes = []
    for quote in quotes_cursor:
        author_id = str(quote.get("author"))
        author = authors.get(author_id, {"fullname", 'unknown'})
        quote["author"] = author
        quote["author_id"] = author_id
        quote["author_idn"] = author['_id']
        quote["tags"] = quote.get("tags", [])
        quotes.append(quote)
    paginator = Paginator(range(total_quotes), per_page)
    page_obj = paginator.get_page(page)

    tags_cursor = db.quotes.aggregate([
        {"$unwind": "$tags"},
        {"$group" : {"_id": "$tags", "quote_count" : {"$sum" : 1}}},
        {"$sort": {"quote_count": -1}},
        {"$limit": 10}
    ])
    popular_tags = []

    for tag in tags_cursor:
        popular_tags.append({'name': tag['_id']})

    return {
        "authors": authors,
        "quotes": quotes,
        "page_obj": page_obj,
        "paginator": paginator,
        "popular_tags": popular_tags,
    }

from django.db.models import Count

def get_data_from_postgres(page=1, per_page=10):
    authors = {str(author.id): author for author in Author.objects.all()}

    quotes_objects = Quote.objects.prefetch_related('tags', 'author')
    paginator = Paginator(quotes_objects, per_page)

    try:
        page_obj = paginator.get_page(page)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    popular_tags = Tag.objects.annotate(quote_count=Count('quotes')).order_by('-quote_count')[:10]

    quotes = []
    for quote in page_obj:
        quotes.append({
            "quote": quote.quote,
            "author": {
                "id": str(quote.author.id),
                "fullname": quote.author.fullname,
                "born_date": quote.author.born_date,
                "born_location": quote.author.born_location,
                "description": quote.author.description,
            },
            "tags": [tag.name for tag in quote.tags.all()]
        })

    return {
        'authors': authors,
        'page_obj': page_obj,
        'quotes': quotes,
        'paginator': paginator,
        'popular_tags': popular_tags,
    }
