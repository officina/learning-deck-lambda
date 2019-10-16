import json
from gamecontroller import handler as GameController


def user_status_action(event, context):
    print(event)
    result = GameController.user_status_action(event, context)
    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }
    print(response)
    return response


def play_action(event, context):
    result = GameController.play_action(event, context)

    response = {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    }

    print(response)
    return response


def play_app_action(event, context):
    result = GameController.play_app_action(event, context)
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

    print(response)
    return response


def get_lazy_users(event, context):

    result = GameController.get_lazy_users(event, context)
    response = {
        'statusCode': 200,
        'body': json.dumps(result)
    }
    print(response)
    return response

def reset_players(event, context):
    print(event)
    GameController.reset_players()


def auth(event, context):
    print(event)
    return GameController.auth(event, context)


def get_auth_token(event, context):
    print(event)
    return GameController.get_auth_token(event, context)
