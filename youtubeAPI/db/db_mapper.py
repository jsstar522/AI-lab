import db.simple_dynamo_db
import db.simple_mongo_db
import json
import copy
import random, time
import yaml, logging
from bson.objectid import ObjectId
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

class DBMapper:
    RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                        'ThrottlingException')

    def __init__(self, _json_file_path="db/config.json", _status="development", _chosen_db="dynamodb"):

        # Construct the logger named DBMapper aka class name
#        with open('debug_config.yml', 'r') as f:
#            config = yaml.safe_load(f.read())
#            logging.config.dictConfig(config)
#        self.logger = logging.getLogger('db_logger.{0}'.format(self.__class__.__qualname__))

        # Read the json configuration file
        with open(_json_file_path, encoding='UTF8') as f:
            self.data = json.load(f)

        self.chosen_db = _chosen_db
        self.configure = copy.deepcopy(self.data['configure'])
        self.selected_db = copy.deepcopy(self.data[_status][self.chosen_db])
        self.primary_key = self.configure['tableInfo']['primaryKey']
        self.retries=0
        self.info = copy.deepcopy(self.configure['tableInfo']['tableAttr'])

        if self.chosen_db is "localhost":
            pass
        elif self.chosen_db is "mongodb":
            self.db = db.simple_mongo_db.SimpleMongoDB(self.configure, self.selected_db)
        elif self.chosen_db is "dynamodb":
            self.db = db.simple_dynamo_db.SimpleDynamoDB(self.configure, self.selected_db)

    def init(self):
        self.retries=0
        self.configure = copy.deepcopy(self.data['configure'])
        self.info = copy.deepcopy(self.configure['tableInfo']['tableAttr'])

    """ CRUD Operations
    """
    def select(self, _dict):  # READ
        if self.chosen_db is "mongodb":
            # return self.db.collection.find({self.primary_key: _dict[self.primary_key]})
            return self.db.collection.find(_dict)
        elif self.chosen_db is "dynamodb":
            """ I used query() method here.
            It returns list even if any items don't exist
            
            get_item() method returns object.
            But get_item() returns Error if item does not exist.
            """
#            self.logger.debug(self.db.table.creation_date_time)
#            self.logger.debug(self.primary_key, _dict[self.primary_key])
            table_scan = self.retry_exception("select", _dict)
#            self.logger.debug(table_scan)
            return table_scan

    def insert(self, _dict):  # CREATE
        self.put_items(_dict)
#        self.logger.debug(self.info)
        if self.chosen_db is "mongodb":
            self.db.collection.insert_one(self.info)
            self.init()
        elif self.chosen_db is "dynamodb":
            self.retry_exception("insert", _dict)
            for attr_key in self.configure['tableInfo']['tableAttr']:
                if attr_key in self.info:
                    continue
                self.info[attr_key] = copy.deepcopy(self.configure['tableInfo']['tableAttr'][attr_key])

    def update(self, _dict):  # UPDATE, SET
        self.put_items(_dict)
        if self.chosen_db is "mongodb":
            self.db.collection.update({self.primary_key: self.info[self.primary_key]}, {"$set": self.info}, True)
        elif self.chosen_db is "dynamodb":
            self.retry_exception("update", _dict)

    def delete(self, _dict):  # DELETE
        if self.chosen_db is "mongodb":
            self.db.collection.delete_one({self.primary_key: _dict[self.primary_key]})
        elif self.chosen_db is "dynamodb":
            self.retry_exception("delete", _dict)

    def put_items(self, _dict):
        for key in _dict:
            self.info[key] = _dict[key]
            self.configure['tableInfo']['tableAttr'][key] = _dict[key]
        if self.chosen_db is "dynamodb":
            # for web authentification, primary key must be String
            self.info[self.primary_key] = str(self.info[self.primary_key])

            # To avoid iteration error
            # ref: https://stackoverflow.com/a/11941855
            for key in list(self.info):
                if self.info[key] == '':
                    del self.info[key]
                elif type(self.info[key]) is list and len(self.info[key]) == 0:
                    del self.info[key]

    def retry_exception(self, _str, _dict={}):
        # exponential-backoff-and-jitter
        # https://gist.github.com/shentonfreude/8d26ca1fc93fdb801b2c
        while True:
            try:
                if _str == "select":
                    result = self.db.table.query(
                        KeyConditionExpression=Key(self.primary_key).eq(str(_dict[self.primary_key]))
                    )
                    return result
                elif _str == "insert":
                    self.db.table.put_item(
                        Item=self.info,
                    )
                elif _str == "update":
                    self.db.table.update_item(
                        Key={self.primary_key: _dict[self.primary_key]},
                        UpdateExpression=self.db.set_update_expression(_dict),
                        ExpressionAttributeNames=self.db.generate_expression_attribute_names(_dict),
                        ExpressionAttributeValues=self.db.generate_expression_attribute_values(_dict)
                    )
                elif _str == "delete":
                    self.db.table.delete_item(
                        Key={self.primary_key: _dict[self.primary_key]},
                        ConditionExpression="attribute_exists(%s)" % (self.primary_key)
                    )
                self.retries = 0
                break
            except ClientError as err:
                if err.response['Error']['Code'] not in DBMapper.RETRY_EXCEPTIONS:
                    raise
#                self.logger.debug('WHOA, too fast, slow it down retries={0}'.format(self.retries))
                # sleep(2 ** self.retries)
                # fulljitter : https://aws.amazon.com/ko/blogs/architecture/exponential-backoff-and-jitter/
                fulljitter = random.uniform(0, 2 ** self.retries)
                time.sleep(fulljitter)
                self.retries += 1     # TODO max limit

    def is_exist(self, _dict) -> bool:
        if self.chosen_db is "mongodb":
            return True if self.select(_dict).count() > 0 else False
        elif self.chosen_db is "dynamodb":
            return True if len(self.select(_dict)['Items']) > 0 else False
