# coding: utf-8

import json
from datetime import datetime
import os
import boto3

from .playoff import Playoff, PlayoffException

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
    print("Client Playoff creation with ref-time " + str(datetime.now()))
    if state == 'READY':
        CLIENT_ID = os.environ.get('PLAYOFF_CLIENT_ID_READY')
        CLIENT_SECRET = os.environ.get('PLAYOFF_CLIENT_SECRET_READY')
        po_state = "ready"
    else:
        CLIENT_ID = os.environ.get('PLAYOFF_CLIENT_ID_PUBLISHED')
        CLIENT_SECRET = os.environ.get('PLAYOFF_CLIENT_SECRET_PUBLISHED')
        po_state = "published"

    print(CLIENT_ID)

    client = Playoff(
        hostname=HOSTNAME,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        type="client",
        store=lambda token: Token.set_token_dynamo(token, po_state),
        load=lambda: Token.get_token_dynamo(po_state),
    )
    print("Creation OK with ref-time " + str(datetime.now()))
    return client


def get_real_players_count(state='PUBLISHED'):

    if state == 'READY':
        table_name = os.environ.get('DYNAMODB_USERS_READY_INFO_TABLE')
    else:
        table_name = os.environ.get('DYNAMODB_USERS_INFO_TABLE')

    response = boto3.client('dynamodb').describe_table(
        TableName=table_name
    )

    index = [x for x in response['Table']['GlobalSecondaryIndexes'] if x['IndexName'] == 'date_last_play-index']
    return index[0]['ItemCount']


def get_user_status(event, context, player, playoff_client, force_update=False):
    print("Get user status - START")
    import socket
    print(f"socket.gethostbyname(\'{HOSTNAME}\') --> {socket.gethostbyname(HOSTNAME)}")
    state_ = "PUBLISHED"
    web_source = False
    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]
    if event["queryStringParameters"] is not None and "SOURCE" in event["queryStringParameters"]:
        print("Source parameter == WEB")
        web_source = event["queryStringParameters"]["SOURCE"] == "WEB"

    # import time
    # if (player == 'caacdb6e6f3f47258b9f0707c35c7f93') and state_ != 'READY':
    #     time.sleep(20)

    try:
        if state_ == 'READY':
            try:
                if not web_source:
                    UserReady.get(player).update_playoff_user_ranking(playoff_client, force_update)
                user_info = UserReady.get(player).update_playoff_user_profile(playoff_client, force_update)
            except UserReady.DoesNotExist:
                print("exception")
                UserReady(player).save()
                UserReady.get(player).update_playoff_user_ranking(playoff_client)
                user_info = UserReady.get(player).update_playoff_user_profile(playoff_client)
        else:
            try:
                if not web_source:
                    User.get(player).update_playoff_user_ranking(playoff_client, force_update)
                user_info = User.get(player).update_playoff_user_profile(playoff_client, force_update)
            except User.DoesNotExist:
                User(player).save()
                User.get(player).update_playoff_user_ranking(playoff_client)
                user_info = User.get(player).update_playoff_user_profile(playoff_client)

    except PlayoffException as err:
        print(err)
        if err.name == 'player_not_found':
            return playoff_player_not_found_error_response(err.message)
        else:
            return playoff_error_response(err.message)

    ranking_info = user_info.playoff_user_ranking_dict_format
    weeks_info = user_info.unblocked_weeks
    user_profile_info = user_info.playoff_user_profile_dict_format
    # nel caso di web_source non calcoliamo il ranking perché non è necessario
    if web_source:
        ranking = -1
    else:
        try:
            total_players = get_real_players_count(state_) + 1
            # total_players = ranking_info['total']
            my_position = ranking_info['data'][0]['rank']
            print(f"Ranking calculation with total players {total_players} and my position {my_position}")
            ranking_ = my_position / total_players
            import math
            ranking = math.floor((1 - ranking_) * 100) / 100
            print(f"Ranking: {ranking_}")
        except Exception as e:
            ranking = 0.99

    date_last_play = user_info.date_last_play_timestamp_format

    print("MAPPING START")
    result = Mapping(user_profile_info, weeks_info, ranking=ranking, date_last_play=date_last_play).json
    print(result)
    if bool(result["body"]["world"]["status"]):
        return result
    else:
        print("Warning - internal retry")
        return get_user_status(event, context, player, playoff_client, True)


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

    print("PLAY ACTION: before get_playoff_client")
    playoff_client = get_playoff_client(state_)
    print("PLAY ACTION: after get_playoff_client")

    if "challengeid" not in event_body:
        return invalid_response("no challenge id specified")

    if "choices" not in event_body or not isinstance(event_body["choices"], list):
        return invalid_response("no choices specified")

    choices = {var['q']: var['a'] for var in event_body['choices']}
    player = event['pathParameters']['player']

    # import time
    # if (player == '015eb2fe2b56489792694693b043d63a') and state_ == 'READY':
    #     time.sleep(50)

    try:
        print("Before post - play_action")
        result_post = playoff_client.post(
            route=f"/runtime/actions/{event_body['challengeid']}/play",
            query={"player_id": player},
            body={
                "variables": choices
            }
        )
        print("******************")
        print("RESULT POST")
        print(result_post)
        print("******************")
        dynamic_points = 0

        for obj in result_post['events']['local'][0]['changes']:
            if obj["metric"]["id"] == 'punti':
                old_val = int(obj["delta"]["old"])
                new_val = int(obj["delta"]["new"])
                dynamic_points = dynamic_points + (new_val - old_val)
                print("Points parziale guadagnato: " + str(new_val - old_val))

        print("Points guadagnati: " + str(dynamic_points))

        if state_ == 'READY':
            try:
                UserReady.get(player).save_last_play()
            except UserReady.DoesNotExist:
                UserReady(player).save()
                UserReady.get(player).save_last_play()
        else:
            try:
                User.get(player).save_last_play()
            except User.DoesNotExist:
                User(player).save()
                User.get(player).save_last_play()

    except PlayoffException as err:
        print(err)
        if err.name == 'player_not_found':
            return playoff_player_not_found_error_response(err.message)
        else:
            return playoff_error_response(err.message)
    result = get_user_status(event, context, player, playoff_client=playoff_client, force_update=True)

    new_result_body = {
        "points": dynamic_points,
        "params": result["body"]["progress"]["params"]
    }

    new_result = dict()
    new_result["statusCode"] = 200
    new_result["body"] = new_result_body
    return new_result


def user_status_action(event, context):
    state_ = "PUBLISHED"

    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]

    if event["queryStringParameters"] is not None and "force_cache_update" in event["queryStringParameters"]:
        force_cache_update = True
        print("Force update required")
    else:
        force_cache_update = False
        print("Force update not required")

    playoff_client = get_playoff_client(state_)
    player = event['pathParameters']['player']
    return get_user_status(event, context, player, playoff_client, force_cache_update)


def level_upgrade_action(event, context):
    event_body = json.loads(event["body"])
    state_ = "PUBLISHED"
    if event["queryStringParameters"] is not None and "state" in event["queryStringParameters"]:
        state_ = event["queryStringParameters"]["state"]

    playoff_client = get_playoff_client(state_)
    player = event['pathParameters']['player']

    # import time
    # if (player == '015eb2fe2b56489792694693b043d63a') and state_ == 'READY':
    #     time.sleep(50)

    map = {
        "casa": 'compra_casa_livello',
        "mobilita": 'compra_mobilita_livello',
        "vita": 'compra_mia_vita_livello',
        "tempo": 'compra_tempo_libero_livello'
    }
    data = json.loads(event["body"])
    key = f'{map[data["id"]]}_{data["newLevel"]}'
    end_point = f'/runtime/actions/{key}/play'
    try:
        result_post = playoff_client.post(end_point, query={"player_id": player},)
    except PlayoffException as err:
        print(err)
        if err.name == 'player_not_found':
            return playoff_player_not_found_error_response(err.message)
        else:
            return playoff_error_response(err.message)

    # per ora consideriamo non necessario l'aggiornamento della data eseguendo un level upgrade
    # User.get(player).save_last_play()
    return get_user_status(event, context, player, playoff_client, True)


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
    for user in temp_users:
        users += [{
            'user_id': user.user_id,
            'lastPlayed': user.date_last_play_timestamp_format
        }]

    return users


def reset_players():
    print('Reset dei players in ready')
    TABLE_NAME = 'users_info_ready-prod'

    playoff_client = get_playoff_client('READY')

    client_db = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USERS_READY_INFO_TABLE'])

    while True:
        response = playoff_client.get(route='/admin/players')
        if len(response['data']) == 0:
            break;
        print(response['data'])
        for player in response['data']:
            player_target = player['id']
            playoff_client.delete(route=f'/admin/players/{player_target}')
            key = dict()
            key["user_id"] = player_target
            client_db.delete_item(Key=key)
            print(f'player {player_target} deleted')

    #ricreo il nuovo set di players
    for i in range(1, 30):
        player = f'player_{i}'
        response = playoff_client.post(route='/admin/players', body={'id': player, 'alias': player})
        item = {
            "user_id": player
        }
        print("Player creato: " + player)


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

