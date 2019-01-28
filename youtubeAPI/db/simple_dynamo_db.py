import boto3

class SimpleDynamoDB:
    def __init__(self, _configure, _selected_db):
        # Get the service resource.
        self.dynamodb = boto3.resource('dynamodb')
        self.configure = _configure
        self.selected_db = _selected_db

        self.join_table(boto3.client('dynamodb').list_tables()['TableNames'])

    def join_table(self, _table_names):
        if self.configure['tableName'] in _table_names:
            self.table = self.dynamodb.Table(self.configure['tableName'])
        else:
            print('%s does not exist' % self.configure['tableName'])
            # Create the DynamoDB table like below.
            self.table = self.dynamodb.create_table(
                TableName=self.configure['tableName'],
                KeySchema=[
                    {
                        "AttributeName": self.configure['tableInfo']['primaryKey'],
                        "KeyType": 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        "AttributeName": self.configure['tableInfo']['primaryKey'],
                        "AttributeType": 'S'  # String
                    },
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            )
            # Wait until the table exists.
            self.table.meta.client.get_waiter('table_exists').wait(TableName=self.configure['tableName'])

    def generate_expression_attribute_names(self, _dict):
        values = {}
        for key in _dict:
            if self.is_primary_key(key):
                continue
            values["#{0}".format(key)] = key 
        return values

    def generate_expression_attribute_values(self, _dict):
        values = {}
        for key in _dict:
            if self.is_primary_key(key):
                continue
            values[":{0}".format(key)] = _dict[key] 
        return values

    def set_update_expression(self, _dict):
        expression = 'SET'
        for key in _dict:
            if self.is_primary_key(key):
                continue
            expression += ' #{0} = :{0},'.format(key)
        expression = expression[:-1]
        return expression
    
    def is_primary_key(self, _key):
        pk = self.configure['tableInfo']['primaryKey']
        if pk == _key:
            return True
        return False

if __name__=='__main__':
    import json
    #def __init__(self, _configure, _selected_db):
    with open("config.json", encoding='UTF8') as f:
        data = json.load(f)

    configure = data['configure']
    selected_db = data['development']['dynamodb']

    db = SimpleDynamoDB(configure, selected_db) 
    print(db.table)
    print(db.table.creation_date_time)
    test = {
        "newsID":172020,
        "title":"hello",
        "author":"bj"
    }
    
    update_expression = db.set_update_expression(_dict=test)
    expression_attribute_names = db.generate_expression_attribute_names(_dict=test)
    expression_attribute_values = db.generate_expression_attribute_values(_dict=test)
    print(update_expression)
    print(expression_attribute_names)
    print(expression_attribute_values)
    
    db.table.update_item(
        Key={"newsID":172020},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="ALL_NEW"
    )
