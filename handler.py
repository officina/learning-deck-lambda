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

    def set_token(self, token):
        f = open('saved_token.txt', 'w')
        s = str(token)
        j = json.dumps(token)
        f.write(j)
        f.close()

        self._token = token
        #print("saving token " + str(token))

    def get_token(self):
        f = open('saved_token.txt', 'r')
        ra = f.read()
        self._token = json.loads(ra)
        f.close()
        #print("returning token " + str(self._token))
        return self._token

    def set_token_dynamo(self, token):
        import boto3
        dynamoDb = boto3.resource('dynamodb')
        client = dynamoDb.Table(tokenTableName)
        response = client.put_item(
            Item={"token":tokenTableName,
                 "access_token":token['access_token'],
                  "token_type":token['token_type'],
                 "expires_at":str(token['expires_at'])
                  }
        )
    def get_token_dynamo(self):
        import boto3
        dynamoDb = boto3.resource('dynamodb')
        client = dynamoDb.Table(tokenTableName)
        response = client.get_item(
            Key={"token":tokenTableName}
        )
        res = response["Item"]
        d = {
            "access_token":res['access_token'],
            "token_type":res['token_type'],
            "expires_at":res['expires_at']

         }

        return d




def play_action(event, context):
    token_storer = TokenStorer()

    pl = Playoff(
        client_id=client_id,
        client_secret=client_secret,
        type="client",
        allow_unsecure=True,
        store=lambda token: token_storer.set_token_dynamo(token),
        load=lambda: token_storer.get_token_dynamo()
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



