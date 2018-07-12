import boto3
from playoff import Playoff, PlayoffException


# data = {
#     "id": "casa",
#     "newLevel": "1"
# }
#
# map = {
#         "casa": 'compra_casa_livello',
#         "mobilita": 'compra_mobilita_livello',
#         "vita": 'compra_mia_vita',
#         "tempo": 'compra_tempo_libero'
#     }
#
# key = f'{map[data["id"]]}_{data["newLevel"]}'
#
# print(key)

pl = Playoff(
        client_id='M2EzOWU4ZjUtM2Q5Yi00ZmE0LTkxNjYtOWM3MmFkMGNjNTIx',
        client_secret='MDc2ZGE1YjgtM2FjYS00MGYwLTg2YTQtYjY0OWVjNTViNzJjYzg3ZTVlNzAtNTM4OS0xMWU4LTlmMzctMjE2MGI4MDQ1OGMx',
        type="client",
        allow_unsecure=True,
)

print('ok')

# pl.post("/admin/players", body={"id": "player", "alias": "player"})

counter = list(range(1, 201));

for x in counter:
    val = 'player_'+ str(x)
    print(val)
    pl.post("/admin/players", body={"id": val, "alias": val})