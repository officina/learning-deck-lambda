# coding: utf-8

import json
from playoff import Playoff, PlayoffException
import json
import time
import os
from .mapping import Mapping
import boto3

from .dynamo_models import User, Token

CLIENT_ID = os.environ.get('PLAYOFF_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PLAYOFF_CLIENT_SECRET')
HOSTNAME = os.environ.get('PLAYOFF_HOSTNAME')
# Utils


def invalid_response(message):
    return {"statusCode": 400, "body": {"message": message}}


def playoff_player_not_found_error_response(message):
    return {"statusCode": 404, "body": {"message": message}}


def playoff_error_response(message):
    return {"statusCode": 500, "body": {"message": message}}


def get_playoff_client():
    return Playoff(
        hostname=HOSTNAME,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        type="client",
        allow_unsecure=True,
        store=lambda token: Token.set_token_dynamo(token),
        load=lambda: Token.get_token_dynamo(),
    )


def get_user_status(event, context, player, playoff_client):

    result = playoff_client.get(route=f"/admin/players/{player}",)
    result_ranking = playoff_client.get(
        route="/runtime/leaderboards/progressione_personale",
        query={
            "player_id": player,
            "cycle": "alltime",
            "entity_id": player,
            "radius": "0",
            "sort": "descending",
            "ranking": "relative"
        })
    # get_weeks is the only action of Mapping that would require aws, so I leave it here
    ranking = (result_ranking['data'][0]['rank'] / result_ranking['total'] * 100) / 100

    weeks = get_weeks(player)

    return Mapping(result, weeks, ranking=ranking).json


def get_weeks(player):

    try:
        user_player = User.get(player)
        weeks = user_player.unblocked_weeks
    except User.DoesNotExist:
        User(player).save()
        weeks = 1

    return weeks


def generatePolicy(ip, effect, resource):
    auth_response = dict()
    auth_response['principalId'] = 'User'

    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'FirstStatement',
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }

        auth_response['policyDocument'] = policy_document

    return auth_response

#/api/play
#/api/user_status?user_id=<user>

# Funzioni "pubbliche"


def play_action(event, context):
    print(event)
    event_body = json.loads(event["body"])
    playoff_client = get_playoff_client()
    if "challengeid" not in event_body:
        return invalid_response("no challenge id specified")

    if "choices" not in event_body or not isinstance(event_body["choices"], list):
        return invalid_response("no choices specified")

    choices = {var['q']: var['a'] for var in event_body['choices']}
    player = event['pathParameters']['player']

    try:
        result_post = playoff_client.post(
            route=f"/runtime/actions/{event_body['challengeid']}/play",
            query={"player_id": player},
            body={
                "variables": choices
            }
        )
    except PlayoffException as err:
        if err.name == 'player_not_found':
            return playoff_player_not_found_error_response(err.message)
        else:
            return playoff_error_response(err.message)

    return get_user_status(event_body, context, player, playoff_client=playoff_client)


def user_status_action(event, context):
    playoff_client = get_playoff_client()
    player = event['pathParameters']['player']
    return get_user_status(event, context, player, playoff_client)


def level_upgrade_action(event, context):

    playoff_client = get_playoff_client()
    player = event['pathParameters']['player']
    map = {
        "casa": 'compra_casa_livello',
        "mobilita": 'compra_mobilita_livello',
        "vita": 'compra_mia_vita_livello',
        "tempo": 'compra_tempo_libero_livello'
    }
    data = json.loads(event["body"])
    key = f'{map[data["id"]]}_{data["newLevel"]}'
    end_point = f'/runtime/actions/{key}/play'

    result_post = playoff_client.post(end_point, query={"player_id": player},)
    return get_user_status(event, context, player, playoff_client)


def auth(event, context):
    print(event)
    caller_ip = event['headers']['X-Forwarded-For']
    dynamo_db = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_IP_AUTH_TABLE'])
    key = dict()
    key["ip"] = caller_ip
    response_result = dynamo_db.get_item(Key=key)
    return generatePolicy(1, 'Allow', event['methodArn'])
    # if "Item" in response_result:
    #     print(f'{caller_ip} authorized')
    #     return generatePolicy(caller_ip, 'Allow', event['methodArn'])
    # else:
    #     print(f'{caller_ip} unauthorized')
    #     return generatePolicy(caller_ip, 'Deny', event['methodArn'])
