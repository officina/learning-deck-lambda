import json
from playoff import Playoff, PlayoffException
import json
import time
import os
from gamecontroller import handler as GameController
import simplejson as sjson


def user_status_action(event, context):
    result = GameController.user_status_action(event, context)
    response = {
        'statusCode': 200,
        "body": json.dumps(result['body'])
    }
    return response

def get_user_status(event, context):
    print("*************************************")
    print(event)
    print("*************************************")
    print(context)
    print("*************************************")
    body = {
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

def play_action(event, context):
    print("*************************************")
    print(event)
    print("*************************************")
    print(context)
    print("*************************************")
    body = {
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def user_upgrade(event, context):
    print("*************************************")
    print(event)
    print("*************************************")
    print(context)
    print("*************************************")
    body = {
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
