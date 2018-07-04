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
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }
    return response


def play_action(event, context):
    result = GameController.play_action(event, context)
    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }
    return response


def level_upgrade(event, context):

    result = GameController.level_upgrade_action(event, context)
    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }
    return response
