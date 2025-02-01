from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from quotes.models import Author, Quote, Tag
import json
import re
import requests

MAIN_URL = 'http://localhost:8000'
author_details = []
quotes_data_arr = []

def get_curr_dir():
    return Path(__file__).resolve().parent

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    return soup

def decode_text(text):
    text = text.strip()
    symbols_to_replace = ['\u201c', '\u201d']
    pattern = "[" + re.escape("".join(symbols_to_replace)) + "]"
    text = re.sub(pattern, '', text)

    return text

def get_author_details(author_link):
    author_soup = get_soup(author_link)
    author_fullname = author_soup.find('h3', class_='author-title')
    if not author_fullname:
        author_fullname = author_soup.find('span', class_='author-title')
    fullname = decode_text(author_fullname.text)

    author_born_date = author_soup.find('span', class_='author-born-date')
    if not author_born_date:
        author_born_date = author_soup.find('kbd', class_='author-born-date')
    born_date = decode_text(author_born_date.text)

    author_born_location = author_soup.find('span', class_='author-born-location')
    if not author_born_location:
        author_born_location_text = 'not found'
    else:
        author_born_location_text = author_born_location.text
    born_location = decode_text(author_born_location_text.strip())

    author_description = author_soup.find('div', class_='author-description')
    if not author_description:
        author_description = author_soup.find('p', class_='author-description')
    description = decode_text(author_description.text)

    author_data = {
        "fullname": decode_text(fullname),
        "born_date": born_date,
        "born_location": born_location,
        "description": decode_text(description)
    }

    return author_data

def get_quotes_data(link):
    main_soup = get_soup(link)
    quotes = main_soup.find_all('span', class_='text')
    authors = main_soup.find_all('small', class_='author')
    tags = main_soup.find_all('div', class_='tags')

    for i in range(0, len(quotes)):
        tagsforquote = tags[i].find_all('a', class_='tag')

        tags_arr = []
        for tagforquote in tagsforquote:
            print("From get quotes data. Tag: " + tagforquote.text + "\n")
            tags_arr.append(tagforquote.text)
        print("From get quotes data. Author: " + authors[i].text + "\n")
        print("From get quotes data. Quote: " + quotes[i].text + "\n")
        quote_data = {
            "tags": tags_arr,
            "author": authors[i].text,
            "quote": decode_text(quotes[i].text)
        }
        quotes_data_arr.append(quote_data)

    return quotes_data_arr

def get_data(page):
    url = MAIN_URL

    if (page > 1):
        url = MAIN_URL + '/' + str(page)

    main_soup = get_soup(url)

    quotes = main_soup.find_all('span', class_='text')
    authors = main_soup.find_all('small', class_='author')

    if quotes:

        for quote in quotes:
            print(quote.text)

        for author in authors:
            print(author.text)
            about_link = author.find_next_sibling("a")
            link = str(about_link).split('"')[1]

            full_author_link = MAIN_URL + link
            author_data = get_author_details(full_author_link)

            exists = any(item['fullname'] == author.text for item in author_details)

            if not exists:
                author_details.append(author_data)

        if not get_quotes_data(url):
            return
        else:
            page += 1
            get_data(page)

        print(f"curr page is: {page}\n")
        return True
    else:
        print("no data parsed")
        return False

def create_json_files():
    get_data(1)
    with open(get_curr_dir().joinpath('authors.json'), 'w', encoding='utf-8') as f:
        json.dump(author_details, f, ensure_ascii=False, indent=4)
    with open(get_curr_dir().joinpath('quotes.json'), 'w', encoding='utf-8') as f:
        json.dump(quotes_data_arr, f, ensure_ascii=False, indent=4)

def add_to_postgres():
    with open(get_curr_dir().joinpath('authors.json'), 'r', encoding='utf-8') as f:
        authors = json.load(f)
        for author in authors:
            Author.objects.get_or_create(
                fullname=author['fullname'],
                born_date=author['born_date'],
                born_location=author['born_location'],
                description=author['description']
            )
    with open(get_curr_dir().joinpath('quotes.json'), 'r', encoding='utf-8') as f:
        quotes = json.load(f)
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
                author = Author.objects.get(fullname=quote['author'])
                now = datetime.now()
                timestamp = now.timestamp()
                q = Quote.objects.create(
                    author_id=author.id,
                    quote=quote['quote'],
                )
                q.save()
                for tag in tags:
                    q.tags.add(tag)
