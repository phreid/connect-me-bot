from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:admin@cluster0.1eosr.mongodb.net/retryWrites=true&w=majority")
db = client.dev

def add_user(user_id):
    new_user = {
        'userid' : user_id
    }

    db.users.insert_one(new_user)

def get_user(user_id):
    result = db.users.find_one({'userid':user_id})
    return result