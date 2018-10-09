import json
from playoff import Playoff, PlayoffException
import json
import time
import os
from gamecontroller import handler as GameController
import simplejson as sjson


def user_status_action(event, context):
    print(event)
    result = GameController.user_status_action(event, context)
    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }
    return response


def play_action(event, context):
    result = GameController.play_action(event, context)

    # response_temp = {
    #     "points": 27,
    #     "params":
    #         {
    #             "sicurezza": 0.37,
    #             "salute": 0.74,
    #             "sostenibilita": 0,
    #             "risparmio": 0.51
    #         }
    # }
    # attenzione deve ritonrare response, il temp  momentaneamente per una response statica
    # response = {
    #     'statusCode': '200',
    #     'body': json.dumps(response_temp)
    # }

    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }

    print(response)

    return response


def level_upgrade(event, context):
    print(event)
    result = GameController.level_upgrade_action(event, context)
    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }
    return response


def get_lazy_users(event, context):

    result = GameController.get_lazy_users(event, context)
    response = {
        'statusCode': 200,
        'body': json.dumps(result)
    }
    return response

def reset_players(event, context):
    print(event)
    GameController.reset_players()


def auth(event, context):
    print(event)
    return GameController.auth(event, context)

