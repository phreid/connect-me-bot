import os
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter

import database as db

credentials = open('credentials.txt').readlines()
token = credentials[0]
secret = credentials[1]

app = Flask(__name__)
events_adapter = SlackEventAdapter(secret, '/slack/events', app)

web_client = WebClient(token=token)

@events_adapter.on("app_home_opened")
def home_opened(payload):
    event = payload.get("event", {})
    channel = event.get("channel")
    user = event.get("user")

    if db.get_user(user) == None:
        db.add_user(user)
        web_client.chat_postMessage(channel=channel, text="welcome")

@events_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel = event.get("channel")
    text = event.get("text")
    
    if (text.startswith("!register")):
        web_client.chat_postMessage(channel=channel, text="hello")

if __name__ == '__main__':
    app.run(port=3000)