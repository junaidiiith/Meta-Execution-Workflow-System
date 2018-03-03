from pymongo import MongoClient


class Database:
    def __init__(self):
        self.c = MongoClient()
        self.db = self.c['mydb']

    def add_to_database(self, collection_name, record):
        collection = self.db[collection_name]
        collection.insert_one(record)
        return collection.find_one(record)['_id']

    def delete_record(self, collection_name, record):
        collection = self.db[collection_name]
        collection.delete_many(record)

    def update_record(self, collection_name, old_record, new_record):
        collection = self.db[collection_name]
        collection.update(old_record, {'$set': new_record})

    def find_one_record(self, collection_name, record):
        collection = self.db[collection_name]
        return collection.find_one(record)

    def find_many_records(self, collection_name, record):
        collection = self.db[collection_name]
        return collection.find(record)

    def drop_tables(self):
        d = Database().db
        tables = ["Roles", "Resources", "Actions", "Events", "Conditions", "Workflow", "Tasks",
                "Constants", "Globals","Rules"]
        for table in tables:
            try:
                d[table].drop()
            except:
                pass
