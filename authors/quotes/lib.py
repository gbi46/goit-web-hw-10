from pymongo import MongoClient

def get_mongo_client():
    return MongoClient('mongodb://localhost:27017')

def get_mongo_db(db_name):
    return get_mongo_client()[db_name]

def get_mongo_collection(db_name, collection_name):
    return get_mongo_db(db_name)[collection_name]