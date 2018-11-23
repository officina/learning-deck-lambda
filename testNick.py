import boto3
from playoff import Playoff, PlayoffException


dynamo_db = boto3.resource('dynamodb', aws_access_key_id='AKIAIWXQRNUYRCBS4T5Q',
                             aws_secret_access_key='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')
dynamo_db_client = boto3.client('dynamodb', aws_access_key_id='AKIAIWXQRNUYRCBS4T5Q',
                             aws_secret_access_key='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', region_name="eu-central-1")
dynamo_db.Table('users_info_ready-dev')

key = dict()
key["user_id"] = 'lucia'

# response_result = dynamo_db.Table('users_info_ready-dev').get_item(Key=key)


# client_id che consente di accedere a Playoff
CLIENT_ID = 'MmRiNDUxN2ItZGJkNi00ZWQ1LWIyYWUtNmY4MDM0OGVjZDhm'
# secret_id che consente di accedere a Playoff
CLIENT_SECRET = 'MDRhMDIyMjQtMWMwMi00M2FjLWJhM2YtNTNiMDkwNzllMmMxMjFkYmUxYjAtYmMxYS0xMWU4LWEwNDYtNDczYzAwYjQwN2Q4'
# hostname playoff
HOSTNAME = 'playoffgenerali.it'
# profilo AWS (in credentials) che consente di accedere alla tablla dynamo
AWS_PROFILE = 'mygenerali-prod'
# tabella dynamo da ripulire
TABLE_NAME = 'users_info_ready-prod'

playoff_client = Playoff(
    hostname=HOSTNAME,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    type="client",
    allow_unsecure=True
)

player = 'lucia22'

response = playoff_client.get(
        route="/runtime/leaderboards/progressione_personale",
        query={
            "player_id": player,
            "cycle": "alltime",
            "entity_id": player,
            "radius": "0",
            "sort": "descending",
            "ranking": "relative"
        })

print(response)

