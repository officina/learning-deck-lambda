# coding: utf-8

import json
from playoff import Playoff, PlayoffException
import json
import time
import os
from .mapping import Mapping

from .dynamo_models import User, Token

CLIENT_ID = os.environ.get('PLAYOFF_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PLAYOFF_CLIENT_SECRET')

# Utils


def invalid_response(message):
    return {"statusCode": 400, "body": {"message": message}}


def playoff_player_not_found_error_response(message):
    return {"statusCode": 404, "body": {"message": message}}


def playoff_error_response(message):
    return {"statusCode": 500, "body": {"message": message}}


def get_playoff_client():
    return Playoff(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        type="client",
        allow_unsecure=True,
        store=lambda token: Token.set_token_dynamo(token),
        load=lambda: Token.get_token_dynamo(),
    )


def get_user_status(event, context, player, playoff_client):

    result = playoff_client.get(route=f"/admin/players/{player}",)
    print(result)
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
    ranking = (result_ranking['data'][0]['rank']/result_ranking['total']*100)/100

    weeks = get_weeks(player)

    return Mapping(result, weeks, ranking=ranking).json


def get_weeks(player):

    try:
        user_player = User.get(player)
        weeks = user_player.unblocked_weeks
    except User.DoesNotExist:
        weeks = 1
    return weeks

#/api/play
#/api/user_status?user_id=<user>

# Funzioni "pubbliche"


def play_action(event, context):
    print(event)

    playoff_client = get_playoff_client()
    if "challengeid" not in event:
        return invalid_response("no challenge id specified")

    if "player" not in event:
        return invalid_response("no player specified")

    if "choices" not in event or not isinstance(event["choices"], list):
        return invalid_response("no choices specified")

    choices = {var['q']: var['a'] for var in event['choices']}
    player = event['player']

    try:
        result_post = playoff_client.post(
            route=f"/runtime/actions/{event['challengeid']}/play",
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

    return get_user_status(event, context, player, playoff_client=playoff_client)


def user_status_action(event, context):

    playoff_client = get_playoff_client()
    player = event['queryStringParameters']['player']
    return get_user_status(event, context, player, playoff_client)
