from bson.objectid import ObjectId
from pathlib import Path
from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost")

db = client.local

files_path = Path(__file__).parent

with open(files_path.joinpath("quotes.json"), "r", encoding="utf-8") as fd:
    quotes = json.load(fd)

for quote in quotes:
    author = db.authors.find_one({"fullname": quote['author']})
    if author:
        db.quotes.insert_one({
            "quote": quote['quote'],
            "tags": quote["tags"],
            "author": ObjectId(author['_id'])
        })