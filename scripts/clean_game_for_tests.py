from playoff import Playoff, PlayoffException

print("*************************")
print("INIZIO")
print("*************************")

CLIENT_ID = 'MzM1ODg2OGYtYzkzNy00ZTUwLTlkZjktYjZmMzY3NDc2ZmFj'
CLIENT_SECRET = 'YjIzNmEzY2UtMDc5Yi00ZDE3LTlhNzQtMWM0ZjRkZWM0ZmNiODA0ZGMxYTAtYWMyZi0xMWU4LWIwYmItOWRiOWY3N2UxMTYz'
HOSTNAME = 'playoff.cc'

playoff_client = Playoff(
    hostname=HOSTNAME,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    type="client",
    allow_unsecure=True
)

# for i in range(1, 120):
#     player = f'player_test_{i}'
#     print("creazione player " + player)
#     playoff_client.post(route='/admin/players', body={'id': player, 'alias': player})


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
        print(f'player {player_target} deleted')

print("*************************")
print("FINE")
print("*************************")
