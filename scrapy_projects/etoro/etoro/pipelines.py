# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


import json
from datetime import datetime

import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class EtoroDashboardPipeline:

    timestamp = datetime.now().strftime("%d-%m-%y")

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        collection_name = f"{settings['MONGODB_INVESTOR_COLLECTION']}_{self.timestamp}"
        db = connection[settings['MONGODB_DB']]
        self.collection = db[collection_name]
        db.drop_collection(collection_name)

    def process_item(self, item, spider):
        if spider.name == "etoro_dashboard":
            valid = True
            for data in item:
                if not data:
                    valid = False
                    raise DropItem("Missing {0}!".format(data))
            if valid:
                self.collection.insert(dict(item))
            return item
        elif spider.name == "etoro_investor":
            pass
