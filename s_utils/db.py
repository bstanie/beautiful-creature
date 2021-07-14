import pymongo

import project_settings


class DataBaseConnector:

    def __init__(self):
        self.connection = pymongo.MongoClient(
            project_settings.MONGODB_SERVER,
            project_settings.MONGODB_PORT)
        self.db = self.connection[project_settings.MONGODB_DB_NAME]
        self.collections = dict()

    def get_collection(self, collection_name):
        if collection_name not in self.collections:
            collection = self.db[collection_name]
            self.collections[collection_name] = collection
        return self.db[collection_name]

    def save_item(self, collection_name, item):
        if len(item) > 0:
            collection = self.get_collection(collection_name)
            collection.insert_many(item)

    def save_items(self, collection_name, items):
        if len(items) > 0:
            collection = self.get_collection(collection_name)
            collection.insert_many(items)

    def delete_items(self, collection_name, query):
        collection = self.get_collection(collection_name)
        collection.delete_many(query)

    def get_items(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find(query)

    @staticmethod
    def make_chunks(data, rows=1000):
        """ Divides the data into 1000 rows each """

        for i in range(0, len(data), rows):
            yield data[i:i + rows]
