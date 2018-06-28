import json
from playoff import Playoff, PlayoffException
import json
import time
import os


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
