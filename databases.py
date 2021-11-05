from pymongo import MongoClient
from uuid import uuid4
import random
import datetime
import requests
from pyairtable import Table
import config

class Database:
    def __init__(self, URL, AIRKEY):
        self.client = MongoClient(URL)
        self.db = self.client.Snipper
        self.users = self.db.users
        self.snips = self.db.snips
        self.table = Table(AIRKEY, config.BASE_ID, 'code')
        
    def addUser(self, email):
        name = requests.get('http://names.drycodes.com/1').json()[0]
        id =str(uuid4())
        self.users.insert_one({
            '_id': id,
            'username': name,
            'email': email,
            'avatar': f'https://avatars.dicebear.com/api/bottts/{id}.svg',
            'snips': [],
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
    
    def userExists(self, email):
        return self.users.find_one({'email': email}) is not None
    
    def getUser(self, email):
        return self.users.find_one({'email': email})
    
    def updateName(self, email, name):
        self.users.update_one({'email': email}, {'$set': {'username': name}})
        return True
    
    def uploadSnip(self, email, snip, name, description, language, theme):
        user = self.getUser(email)
        id = str(uuid4())
        self.snips.insert_one({
            '_id': id,
            'by': user['_id'],
            'name': name,
            'description': description,
            'snip': snip,
            'language': language,
            'theme': theme,
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
        self.table.create({"ID": id, "code": snip})
        self.users.update_one({'_id': user['_id']}, {'$push': {'snips': id}})
        return True