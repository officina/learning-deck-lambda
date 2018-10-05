from playoff import Playoff, PlayoffException
import boto3

print("*************************")
print("INIZIO")
print("*************************")

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


dynamo_db = boto3.session.Session(profile_name=AWS_PROFILE).resource('dynamodb', region_name='eu-central-1')
client_db = dynamo_db.Table(TABLE_NAME)

# for i in range(1, 30):
#     player = f'player_{i}'
#     print("creazione player " + player)
#     response = playoff_client.post(route='/admin/players', body={'id': player, 'alias': player})
#     item = {
#         "user_id": player
#     }
#     client_db.put_item(Item=item)

while True:
    print("aggiorno lista")
    response = playoff_client.get(route='/admin/players')
    if len(response['data']) == 0:
        break;
    print(response['data'])
    for player in response['data']:
        print(player['id'])
        player_target = player['id']
        playoff_client.delete(route=f'/admin/players/{player_target}')
        key = dict()
        key["user_id"] = player_target
        client_db.delete_item(Key=key)
        print(f'player {player_target} deleted')

print("*************************")
print("FINE")
print("*************************")
