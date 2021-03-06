import os
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter

import database as db

credentials = open('credentials.txt').readlines()
token = credentials[0].strip()
secret = credentials[1].strip()

app = Flask(__name__)
events_adapter = SlackEventAdapter(secret, '/slack/events', app)

web_client = WebClient(token=token)

@events_adapter.on('app_home_opened')
def home_opened(payload):
    event = payload.get('event', {})
    channel = event.get('channel')
    user = event.get('user')

    if db.get_user(user) == None:
        db.add_user(user)
        web_client.chat_postMessage(channel=channel, 
            text='hi ::wave::! i\'m connect-me bot! if you\'re part ' +
                'of an underrepresented group, i can help you connect with peers.\n\n' +
                'i recognize the following commands: \n' +
                '\t - !add-to $<group1> $<group2> ... : list yourself as a member of one or more groups. other users can connect with you automatically via dm.\n' +
                '\t - !show-mine: show the groups you\'re listed as a member of\n' +
                '\t - !show-others: show all the available groups, not including any you\'re listed under\n' +
                '\t - !remove-from $<group1> $<group2> ... : remove yourself from one or more groups.\n' +
                '\t - !connect-me $<group>: randomly connect with a user from the group via dm')

@events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel = event.get('channel')
    text = event.get('text')
    user = event.get('user')
    
    if (text.startswith('!add-to')):
        handle_add(user, text, channel)
    if (text.startswith('!connect-me')):
        handle_connect(user, text, channel)
    if (text.startswith('!remove-from')):
        handle_remove(user, text, channel)
    if (text.startswith('!show-other')):
        handle_show_other(user, channel)
    if (text.startswith('!show-mine')):
        handle_show_mine(user, channel)

def handle_add(user, text, channel):
    tokens = text.split(' ')
    added = []
    for t in tokens:
        if t.startswith('$'):
            result = db.add_group_to_user(t, user)
            if (result.acknowledged):
                added.append(t)

    added_string = ', '.join(added)
    web_client.chat_postMessage(channel=channel, 
        text= 'successfully added you to the following groups: ' + added_string)

def handle_connect(user, text, channel):
    tokens = text.split(' ')
    group_tokens = list(filter(lambda x: x.startswith('$'), tokens))

    if (len(group_tokens) > 1):
        web_client.chat_postMessage(channel=channel, 
        text= 'sorry, i can only connect you to one group at a time')
        return

    if (len(group_tokens) == 0):
        web_client.chat_postMessage(channel=channel, 
        text= 'sorry, i couldn\'t find any groups in your message')
        return
    
    user_to_dm = db.get_random_user(user, group_tokens[0])
    if user_to_dm != None:
        user_to_dm_id = user_to_dm['userid']
        response = web_client.conversations_open(users=[user, user_to_dm_id])

        web_client.chat_postMessage(channel=channel, 
            text = 'connecting you with a user now!')

        post_dm_welcome(response['channel'], group_tokens[0])
    else:
        web_client.chat_postMessage(channel=channel, 
            text = 'sorry, i couldn\'t find any users in that group')

def post_dm_welcome(channel, group):
    channel_id = channel['id']

    web_client.chat_postMessage(channel=channel_id, 
        text = 'hi! i\'ve connected you two based on the following group: ' + group)
    
def handle_remove(user, text, channel):
    tokens = text.split(' ')
    removed = []
    for t in tokens:
        if t.startswith('$'):
            result = db.remove_group_from_user(t, user)
            if (result.acknowledged):
                removed.append(t)

    removed_string = ', '.join(removed)
    web_client.chat_postMessage(channel=channel, 
        text= 'successfully removed you from the following groups: ' + removed_string)

def handle_show_other(user, channel):
    groups = db.get_other_groups(user)

    group_string = ', '.join(groups)
    web_client.chat_postMessage(channel=channel, 
        text= 'i found the following groups: ' + group_string)

def handle_show_mine(user, channel):
    groups = db.get_user_groups(user)

    group_string = ', '.join(groups)
    web_client.chat_postMessage(channel=channel, 
        text= 'you\'re listed in the following groups: ' + group_string)

if __name__ == '__main__':
    app.run(port=3000)