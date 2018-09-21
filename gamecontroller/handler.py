# coding: utf-8

import os
import json
import time
from datetime import datetime
import os
from .mapping import Mapping
import boto3

from playoff import Playoff, PlayoffException

from .mapping import Mapping
from .dynamo_models import User, UserReady, Token

HOSTNAME = os.environ.get('PLAYOFF_HOSTNAME')
# Utils


def invalid_response(message):
    return {"statusCode": 400, "body": {"message": message}}


def playoff_player_not_found_error_response(message):
    return {"statusCode": 404, "body": {"message": message}}


def playoff_error_response(message):
    return {"statusCode": 500, "body": {"message": message}}


def get_playoff_client(state='PUBLISHED'):

    if state == 'READY':
        CLIENT_ID = os.environ.get('PLAYOFF_CLIENT_ID_READY')
        CLIENT_SECRET = os.environ.get('PLAYOFF_CLIENT_SECRET_READY')
    else:
        CLIENT_ID = os.environ.get('PLAYOFF_CLIENT_ID_PUBLISHED')
        CLIENT_SECRET = os.environ.get('PLAYOFF_CLIENT_SECRET_PUBLISHED')


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

    state_ = "PUBLISHED"
    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]
    result = playoff_client.get(route=f"/admin/players/{player}")
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

    weeks = get_weeks(player, state_)
    if state_ == 'READY':
        date_last_play = UserReady.get(player).date_last_play_timestamp_format
    else:
        date_last_play = User.get(player).date_last_play_timestamp_format

    return Mapping(result, weeks, ranking=ranking, date_last_play=date_last_play).json


def get_weeks(player, state="PUBLISHED"):
    if state == "READY":
        try:
            user_player = UserReady.get(player)
            weeks = user_player.unblocked_weeks
        except UserReady.DoesNotExist:
            UserReady(player).save()
            weeks = 1
    else:
        try:
            user_player = User.get(player)
            weeks = user_player.unblocked_weeks
        except User.DoesNotExist:
            User(player).save()
            weeks = 1
    return weeks


def generate_policy(ip, effect, resource):
    auth_response = dict()
    auth_response['principalId'] = ip

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
    state_ = "PUBLISHED"
    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]

    playoff_client = get_playoff_client(state_)
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
        if state_ == 'READY':
            UserReady.get(user_id=player, state=state_).save_last_play()
        else:
            User.get(user_id=player, state=state_).save_last_play()
    except PlayoffException as err:
        print(err)
        if err.name == 'player_not_found':
            print(1)
            return playoff_player_not_found_error_response(err.message)
        else:
            print(2)
            return playoff_error_response(err.message)
    print(3)
    return get_user_status(event_body, context, player, playoff_client=playoff_client)


def user_status_action(event, context):
    state_ = "PUBLISHED"

    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]

    playoff_client = get_playoff_client(state_)
    player = event['pathParameters']['player']
    return get_user_status(event, context, player, playoff_client)


def level_upgrade_action(event, context):
    event_body = json.loads(event["body"])
    state_ = "PUBLISHED"
    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]
    playoff_client = get_playoff_client(state_)
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
    # per ora consideriamo non necessario l'aggiornamento della data eseguendo un level upgrade
    # User.get(player).save_last_play()
    return get_user_status(event, context, player, playoff_client)


def get_lazy_users(event, context):
    """return a list of player that played last time before 'from'
    'from' is passed as a parameter
    """
    print(event)
    state_ = "PUBLISHED"
    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]
    from_iso = event['pathParameters']['from']
    from_date = datetime.strptime(from_iso, '%Y-%m-%d')
    users = []

    if state_ == "READY":
        temp_users = UserReady.get_lazy_users(from_date)
    else:
        temp_users = User.get_lazy_users(from_date)
    print(temp_users)
    for user in temp_users:
        users += [{
            'user_id': user.user_id,
            'lastPlayed': user.date_last_play_timestamp_format
        }]

    return users


def auth(event, context):
    print(event)
    # necessario lo split, vedi qui:
    # https://stackoverflow.com/questions/33062097/how-can-i-retrieve-a-users-public-ip-address-via-amazon-api-gateway-lambda-n
    caller_ip = event['headers']['X-Forwarded-For'].split(",")[0]
    dynamo_db = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_IP_AUTH_TABLE'])
    key = dict()
    key["ip"] = caller_ip
    response_result = dynamo_db.get_item(Key=key)
    # return generatePolicy(1, 'Allow', event['methodArn'])
    if "Item" in response_result:
        print(f'{caller_ip} authorized')
        return generate_policy(caller_ip, 'Allow', event['methodArn'])
    else:
        print(f'{caller_ip} unauthorized')
        return generate_policy(caller_ip, 'Deny', event['methodArn'])

