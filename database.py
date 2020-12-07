from pymongo import MongoClient, collection
import random

client = MongoClient('mongodb+srv://admin:admin@cluster0.1eosr.mongodb.net/retryWrites=true&w=majority')
db = client.dev

def add_user(user_id):
    new_user = {
        'userid' : user_id
    }

    db.users.insert_one(new_user)

def get_user(user_id):
    result = db.users.find_one({'userid':user_id})
    return result

def add_group_to_user(group, user_id):
    result = db.users.update_one({'userid':user_id}, 
        {'$addToSet': {'groups' : group}})

    return result

def get_random_user(user, group):
    result = db.users.find({'groups' : group, 'userid': {'$ne': user}})
    count = db.users.count_documents({'groups' : group, 'userid': {'$ne': user}})

    if (count != 0):
        index = random.randrange(count)
        document = result[index]
        return document

def remove_group_from_user(group, user_id):
    result = db.users.update_one({'userid':user_id}, 
        {'$pull': {'groups' : group}})

    return result

def get_other_groups(user):
    user_groups = set()
    user_result = db.users.find({'userid': user})

    for record in user_result:
        groups = record['groups']
        for group in groups:
            user_groups.add(group)

    other_groups = set()
    other_result = db.users.find({'userid': {'$ne': user}})

    for record in other_result:
        groups = record['groups']
        for group in groups:
            if group not in user_groups:
                other_groups.add(group)

    return other_groups

def get_user_groups(user):
    user_groups = set()
    user_result = db.users.find({'userid': user})

    for record in user_result:
        groups = record['groups']
        for group in groups:
            user_groups.add(group)

    return user_groups
