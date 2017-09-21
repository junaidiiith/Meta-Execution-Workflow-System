from pymongo import MongoClient


class Database:
    def __init__(self):
        self.c = MongoClient()
        self.db = self.c['mydb']

    def add_to_database(self, collectionName, record):
        collection = self.db[collectionName]
        collection.insert_one(record)

    def delete_record(self, collectionName, record):
        collection = self.db[collectionName]
        collection.delete_many(record)

    def update_record(self, collectionName, oldrecord, newrecord):
        collection = self.db[collectionName]
        collection.update(oldrecord, {'$set':newrecord})

    def find_one_record(self, collectionName, record):
        collection = self.db[collectionName]
        return collection.find_one(record)

    def find_many_records(self, collectionName, record):
        collection = self.db[collectionName]
        return collection.find(record)