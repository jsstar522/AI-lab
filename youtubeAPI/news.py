from bson.objectid import ObjectId
from mimetypes import guess_extension, guess_type
from urllib.parse import urlsplit, quote
from urllib.request import urlretrieve
import os

from db.db_mapper import DBMapper

class News:
    def __init__(self, _json_file_path="db/config.json", _status="development", _chosen_db="dynamodb"):
        self.mapper = DBMapper(_json_file_path, _status, _chosen_db)

    def init(self):
        self.mapper.init()

    def is_exist(self, _dict):
        if self.mapper.is_exist(_dict):
            return True
        return False

    def set_info(self, _dict):
        if self.is_exist(_dict):
            return
        self.mapper.insert(_dict)
        print(self.mapper.info)
        print("###################set_info###################")

    def set_contents(self):
        self.mapper.update(self.mapper.info)
        print(self.mapper.info)
        print("#####################set_contents###############")

    def add_paragraph(self, _content):
        paragraph = {"line_num": "aaa", "content": str(_content)}
        self.mapper.info["paragraphs"].append(paragraph)
        print(self.mapper.info)

    def delete_item(self, _dict):
        self.mapper.delete(_dict)
