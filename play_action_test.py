from playoff import Playoff, PlayoffException
import json
import time

client_id = 'M2EzOWU4ZjUtM2Q5Yi00ZmE0LTkxNjYtOWM3MmFkMGNjNTIx'
client_secret  ='MDc2ZGE1YjgtM2FjYS00MGYwLTg2YTQtYjY0OWVjNTViNzJjYzg3ZTVlNzAtNTM4OS0xMWU4LTlmMzctMjE2MGI4MDQ1OGMx'


class TokenStorer:
    _token = ''

    # for local development
    def set_token(self, token):
        f = open('saved_token.txt', 'w')
        s = str(token)
        j = json.dumps(token)
        f.write(j)
        f.close()

        self._token = token
        #print("saving token " + str(token))

    # for local development
    def get_token(self):
        f = open('saved_token.txt', 'r')
        ra = f.read()
        self._token = json.loads(ra)
        f.close()
        #print("returning token " + str(self._token))
        return self._token

    # saves the token on dynamodb
    def set_token_dynamo(self, token):
        import boto3
        dynamoDb = boto3.resource('dynamodb')
        client = dynamoDb.Table('playoff_token-dev')
        response = client.put_item(
            TableName='playoff_token-dev',
            Item={"token":"playoff_token",
                 "access_token":token['access_token'],
                  "token_type":token['token_type'],
                 "expires_at":str(token['expires_at'])
                  }
        )
    # retrieves the token from dynamoDB
    def get_token_dynamo(self):
        import boto3
        dynamoDb = boto3.resource('dynamodb')
        client = dynamoDb.Table('playoff_token-dev')
        response = client.get_item(
            TableName='playoff_token-dev',
            Key={"token":"playoff_token"}
        )
        res = response["Item"]
        d = {
            "access_token":res['access_token'],
            "token_type":res['token_type'],
            "expires_at":res['expires_at']

         }

        return d

token_storer = TokenStorer()


def play_action_with_stored_token_retrieval(times):
    t = time.time()
    pl = Playoff(
        client_id=client_id,
        client_secret=client_secret,
        type="client",
        allow_unsecure=True,
        # store=lambda token: token_storer.set_token(token),
        # load=lambda: token_storer.get_token()
        store=lambda token: token_storer.set_token_dynamo(token),
        load=lambda: token_storer.get_token_dynamo()
    )
    for i in range(1, times):
        pl.post(
            route="/runtime/actions/sfida1/play",
            query={"player_id":"max"},
            body={
                    "variables": {
                        "question": 1,
                        "answer": 2
                    }
            }
        )

    t1 = time.time()
    print("elapsed " + str(t1-t))


def play_action_without_stored_token_retrieval(times):
    t = time.time()
    for i in range(1, times):
        pl = Playoff(
            client_id=client_id,
            client_secret=client_secret,
            type="client",
            allow_unsecure=True,

        )

        pl.post(
            route="/runtime/actions/sfida1/play",
            query={"player_id":"max"},
            body={
                    "variables": {
                        "question": 1,
                        "answer": 2
                    }
            }
        )

    t1 = time.time()
    print("elapsed " + str(t1 - t))

def test_with_token(times):
    import requests
    t = time.time()
    for i in range(1, times):
        response = requests.get(
            url="https://wlrp7clawc.execute-api.eu-west-1.amazonaws.com/dev/test/withtoken",
        )
    t1 = time.time()
    print("elapsed " + str(t1 - t))

def test_without_token(times):
    import requests
    t = time.time()
    for i in range(1, times):
        response = requests.get(
            url="https://wlrp7clawc.execute-api.eu-west-1.amazonaws.com/dev/test/withouttoken",
        )
    t1 = time.time()
    print("elapsed " + str(t1 - t))

def play_action_and_get_with_stored_token_retrieval(times):
    t = time.time()
    pl = Playoff(
        client_id=client_id,
        client_secret=client_secret,
        type="client",
        allow_unsecure=True,
        # store=lambda token: token_storer.set_token(token),
        # load=lambda: token_storer.get_token()
        store=lambda token: token_storer.set_token_dynamo(token),
        load=lambda: token_storer.get_token_dynamo()
    )
    for i in range(1, times):
        pl.post(
            route="/runtime/actions/storia01_capitolo01_sfida01/play",
            query={"player_id":"lucia"},
            body={
                    "variables": {
                        "domanda01": 1,
                        "domanda02": 1,
                        "domanda03": 1,
                        "domanda04": 1,
                        "domanda05": 1
                    }
            }
        )

        r1 = pl.get(
            route="/runtime/leaderboards/progressione_personale",
            query={"player_id":"giovanni", "cycle":"alltime", "entity_id":"giovanni", "radius":"0",  "sort":"descending", "ranking":"relative"},
        )

        print(r1)

    t1 = time.time()
    print("elapsed1 " + str(t1-t))

if __name__ == "__main__":
    # play_action_with_stored_token_retrieval(5)
    # play_action_without_stored_token_retrieval(5)
    # TokenStorer().set_token_dynamo(token="abbabba")
    # TokenStorer().get_token_dynamo()
    # test_with_token(10)
    # test_without_token(10)
    play_action_and_get_with_stored_token_retrieval(2)