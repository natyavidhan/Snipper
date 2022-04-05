from pymongo import MongoClient
from uuid import uuid4
import random
import datetime
import requests

class Database:
    def __init__(self, URL, AIRKEY):
        self.client = MongoClient(URL)
        self.db = self.client.Snipper
        self.users = self.db.users
        self.snips = self.db.snips
        
    def addUser(self, email):
        name = requests.get('http://names.drycodes.com/1').json()[0]
        id =str(uuid4())
        self.users.insert_one({
            '_id': id,
            'username': name,
            'email': email,
            'avatar': f'https://avatars.dicebear.com/api/bottts/{id}.svg',
            'snips': [],
            'saves': [],
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
    
    def userExists(self, email):
        return self.users.find_one({'email': email}) is not None
    
    def getUser(self, email):
        return self.users.find_one({'email': email})
    
    def getUserWithId(self, id):
        return self.users.find_one({'_id': id})
    
    def updateName(self, email, name):
        self.users.update_one({'email': email}, {'$set': {'username': name}})
        return True
    
    def uploadSnip(self, email, snip, name, description, language, theme):
        id = str(uuid4())
        user = self.getUser(email)
        self.snips.insert_one({
            '_id': id,
            'by': email,
            'name': name,
            'description': description,
            'snip': snip,
            'language': language,
            'theme': theme,
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
        self.users.update_one({'_id': user['_id']}, {'$push': {'snips': id}})
        return id
    
    def getSnip(self, id):
        snip = self.snips.find_one({'_id': id})
        snip['by'] = self.getUser(snip['by'])
        return snip
        # return 
    
    def getUserSnips(self, email):
        user = self.getUser(email)
        return [self.getSnip(snip) for snip in user['snips']]
    
    def saveSnip(self, snipId, email):
        user = self.getUser(email)
        if snipId in user['saves']:
            return False
        self.users.update_one({'_id': user['_id']}, {'$push': {'saves': snipId}})
        return True
    
    def removeSnip(self, snipId, email):
        user = self.getUser(email)
        if snipId not in user['saves']:
            return False
        self.users.update_one({'_id': user['_id']}, {'$pull': {'saves': snipId}})
        return True
    
    def delteSnip(self, snipId, email):
        user = self.getUser(email)
        self.snips.delete_one({'_id': snipId})
        self.users.update_one({'_id': user['_id']}, {'$pull': {'snips': snipId}})
    
    def get10RandomSnips(self):
        snips = self.snips.aggregate([
            {'$sample': {'size': 10}}
        ])
        return list(snips)