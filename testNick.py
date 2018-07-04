import boto3

data = {
    "id": "casa",
    "newLevel": "1"
}

map = {
        "casa": 'compra_casa_livello',
        "mobilita": 'compra_mobilita_livello',
        "vita": 'compra_mia_vita',
        "tempo": 'compra_tempo_libero'
    }

key = f'{map[data["id"]]}_{data["newLevel"]}'

print(key)