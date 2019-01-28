from pymongo import MongoClient

class SimpleMongoDB:
    def __init__(self, _configure, _selected_db):
        """ Instance for mapping client database to this project

        Connection to MongoDB localhost which is a client-side

        usage:

            for localhost:
                client = MongoClient('mongodb://localhost:27017')
                db = client['trend']  # client['trend'] === client.trend

            for mLab:
                client = MongoClient('mongodb://ds145474.mlab.com:45474')
                auth = client['trend'].authenticate(state["user"]["id"],state["user"]["pw"])
                db = client['trend']

        Connection to mLab which is database as a service
        environments: {
            storage limit: 500 MB
        }
        """
        client = MongoClient(_selected_db['uri'])
        if ("mlab" in _selected_db['uri']):
            auth = client['trend'].authenticate(_selected_db['user']['id'], _selected_db['user']['pw'])
        db = client['trend']  # client['trend'] === client.trend

        """ Define collection(table)
        
        NoSQL feature
            1. Save all attributes(fields) into single document 
        """
        self.collection = db[_configure['tableName']]
