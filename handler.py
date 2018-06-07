import json
from playoff import Playoff, PlayoffException
import json
import time
import os

client_id = os.environ.get('PLAYOFF_CLIENT_ID')
client_secret  =os.environ.get('PLAYOFF_CLIENT_SECRET')
tokenTableName = os.environ.get('DYNAMODB_TOKEN_TABLE')


class TokenStorer:
    _token = ''

    def set_token_dynamo(self, token):
        import boto3
        dynamo_db = boto3.resource('dynamodb')
        client = dynamo_db.Table(tokenTableName)
        response = client.put_item(
            Item={
                    "token": tokenTableName,
                    "access_token": token['access_token'],
                    "token_type": token['token_type'],
                    "expires_at": str(token['expires_at'])
                  }
        )
    def get_token_dynamo(self):
        import boto3
        dynamo_db = boto3.resource('dynamodb')
        client = dynamo_db.Table(tokenTableName)
        response = client.get_item(
            Key={"token": tokenTableName}
        )
        res = response["Item"]
        d = {
            "access_token": res['access_token'],
            "token_type": res['token_type'],
            "expires_at": res['expires_at']

         }

        return d

def invalid_response(message):
    return {"statusCode": 400, "body": {"message":message}}

def playoff_player_not_found_error_response(message):
    return {"statusCode": 404, "body": {"message":message}}

def playoff_error_response(message):
    return {"statusCode": 500, "body": {"message":message}}

def play_action(event, context):
    token_storer = TokenStorer()
    print (event)

    pl = Playoff(
        client_id=client_id,
        client_secret=client_secret,
        type="client",
        allow_unsecure=True,
        store=lambda token: token_storer.set_token_dynamo(token),
        load=lambda: token_storer.get_token_dynamo(),

    )
    if "challengeid" not in event:
        return invalid_response("no challenge id specified")

    if "player" not in event:
        return invalid_response("no player specified")

    if "choices" not in event or not isinstance(event["choices"], list):
        return invalid_response("no choices specified")
    try:

        choices = {}
        for choice in event["choices"]:
            variable = choice["q"]
            value = choice["a"]
            choices[variable] = value


        r = pl.post(
            route="/runtime/actions/"+event["challengeid"]+"/play",
            query={"player_id":event["player"]},
            body={
                    "variables": choices
            }
        )

        result = pl.get(route="/admin/players/"+event["player"],)

        status = {}
        completed_challenges = []
        points = []
        for score in result["scores"]:

            if "metric" in score and "value" in score:
                metric = score["metric"]
                if "type" in metric and "name" in metric:
                    if metric["type"] == 'point' and " totale" not in metric["name"]:
                        status[metric["name"]] = score["value"]


        # e = r["events"]["local"][0]
        #
        # if e["changes"] and isinstance(e["changes"], list):
        #     for change in e["changes"]:
        #         if change["metric"]["type"] == "point":
        #             status[change["metric"]["name"]] = change["delta"]["new"]
        #         elif change["metric"]["type"] == "set":
        #             completed_challenges.append(change["delta"])




        response = {
            "statusCode": 200,
            "playoff_response": r,
            "body": { "world": {
                        "status": status,
                        "points": {
                          "total": 126,
                          "available": 34,
                          "upgrade": {
                            "casa": 45,
                            "mobilita": 15,
                            "vita": 0,
                            "tempo": 60
                          }
                        }
                      },
                      "challenges": {
                        "available": 52,
                        "completed": completed_challenges
                      },
                      "progress": {
                        "ranking": 0.56,
                        "params": {
                          "sicurezza": 0.45,
                          "salute": 0.55,
                          "sostenibilita": 0.76,
                          "risparmio": 0.23
                        }
                      }
                    }
        }

    except PlayoffException as err:

        if err.name == 'player_not_found':
            return playoff_player_not_found_error_response(err.message)
        else:
            return playoff_error_response(err.message)



    return response


def play_action_without_stored_token_retrieval(event, context):


    pl = Playoff(
        client_id=client_id,
        client_secret=client_secret,
        type="client",
        allow_unsecure=True,

    )

    r = pl.post(
        route="/runtime/actions/sfida1/play",
        query={"player_id":"max"},
        body={
                "variables": {
                    "question": 1,
                    "answer": 2
                }
        }
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(r)
    }

    return response



