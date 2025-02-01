from datetime import datetime
from models import Author, Quote
from pathlib import Path
import json

FILES_PATH = Path(__file__).parent

def add_db_data():

    file_name = FILES_PATH.joinpath('authors.json')

    with open(file_name, 'r', encoding='utf-8') as f:
        authors_data = json.load(f)
        for author_data in authors_data:
            author = Author(
                fullname=author_data['fullname'],
                born_date=datetime.strptime(author_data['born_date'], "%B %d, %Y"),
                born_location=author_data['born_location'],
                description=author_data['description']
            )
            author.save()

    file_name = FILES_PATH.joinpath('quotes.json')

    with open(file_name, 'r', encoding='utf-8') as f:
        quotes_data = json.load(f)
        for quote_data in quotes_data:
            author = Author.objects(fullname=quote_data['author']).first()
            if author:
                quote = Quote(
                    tags=quote_data['tags'],
                    author=author,
                    quote=quote_data['quote']
                )
                quote.save()
            else:
                print(f"Author '{quote_data['author']}' not found for quote: {quote_data['quote']}")