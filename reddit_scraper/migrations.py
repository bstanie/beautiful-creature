import datetime
import json
import os
import pathlib

import pymongo
from tqdm import tqdm

import project_settings


def migrate_reddit_json_to_mongo(dir_path):
    connection = pymongo.MongoClient(
        project_settings.MONGODB_SERVER,
        project_settings.MONGODB_PORT)
    db = connection[project_settings.MONGODB_DB_NAME]
    reddit_collection_name = f"{project_settings.MONGODB_REDDIT_COLLECTION}"
    reddit_collection = db[reddit_collection_name]

    for file_name in tqdm(list(os.walk(dir_path))[0][2]):

        try:
            file_path = str(dir_path / f"{file_name}")
            with open(file_path, "r") as f:
                raw_data = json.load(f)
                data = []

                for item in raw_data:
                    if type(item) == list:
                        data.extend(item)
                    else:
                        data.append(item)
                for i in data:
                    i["timestamp"] = datetime.datetime.strptime(i["timestamp"], "%Y-%m-%d %H:%M:%S")
                reddit_collection.insert_many(data)
        except Exception as e:
            print(e, file_name)


if __name__ == "__main__":
    migrate_reddit_json_to_mongo(pathlib.Path(project_settings.PROJECT_ROOT) / "reddit_scraper" / "data")
