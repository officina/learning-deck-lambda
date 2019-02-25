# coding: utf-8
"""
Implementazione del capitolo 6.3.1.1 Questa parte non necessita di aws

"""
import re
from datetime import datetime
from pprint import pprint

RESPONSE = {
    "statusCode": 200,
    "body": {
        "world": {
            "status": {
                "Monete": "20",
                "Punti": "20",
                "Risparmio": "20",
                "Salute": "20",
                "Sicurezza": "30",
                "Sostenibilita": "20"
            },
            "points": {
                "upgrade": {
                    "casa": '<casa_points_to_next_level>, //vedi nota 3',
                    "mobilita": '<high> - <valore_metrica_utente> + 1',
                    "vita": '<high> è valore prelevato dall’oggetto “meta” nello status utente, per la metrica “state” di interesse',
                    "tempo": '<tempo_points_to_next_level>'
                },
                "available": "20",
                "total": "20"
            }
        },
        "challenges": {
            "available": 1,
            "completed": [
                "S01_CH01_C0001"
            ]
        },
        "progress": {
            "ranking": 'TODO',
            "params": {
                "risparmio": '<valore della metrica con id sicurezza_percentuale>',
                "salute": "100",
                "sicurezza": "100",
                "sostenibilita": "100"
            }
        }
    }
}


class Mapping:

    def __init__(self, result, weeks, ranking, date_last_play=0):
        """
        :arg result: il risultato dell'interrogazione dello stato a playoff
        :arg weeks: le settimane sbloccate
        :arg ranking: ranking
        """
        self.result = result
        self.response = RESPONSE.copy()

        self.response['body']['world']['status'] = self.get_status()
        points, available = self.get_points()
        self.response['body']['world']['points'] = points
        self.response['body']['world']['available'] = available
        self.response['body']['world']['points']['upgrade'] = self.upgrade
        self.response['body']['challenges'] = self.get_challenges(weeks)
        self.response['body']['progress']['params'] = self.get_progress()
        self.response['body']['progress']['ranking'] = ranking
        self.response['body']['timestamp'] = int(datetime.now().timestamp())
        self.response['body']['lastPlayed'] = date_last_play

    def get_status(self):

        map = {
            "livelli_casa": 'casa',
            "livelli_mobilita": 'mobilita',
            "livelli_mia_vita": 'vita',
            "livelli_tempo_libero": 'tempo'
        }

        status = {}
        self.upgrade = {}

        temp_values = dict()
        temp_coins = 0

        for score in self.result['scores']:
            if 'metric' in score and score['metric']['id'] == 'monete':
                temp_coins = int(score['value'])
                break

        print(f"temp values {temp_values}")

        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if metric['id'].startswith('livelli_'):
                    key = map[metric['id']]
                    hi = int(score['meta']['high'])
                    lw = int(score['meta']['low'])
                    print(f"Recap per {metric['id']}: hi={hi} lw={lw}")
                    self.upgrade[key] = (hi - lw + 1)

        return status

    def get_points(self):

        total = 0
        available = 0
        points = {'upgrade': {}}
        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if metric['id'] == 'punti':
                    points['total'] = int(score['value'])
                if metric['id'] == 'monete':
                    points['available'] = int(score['value'])

        return points, available

    def get_challenges(self, weeks):

        challenges = []
        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if metric.get('type', None) == 'set':
                    m = re.search('(?P<story_id>\d\d)_.*(?P<ch_id>\d\d)', metric['name'])
                    if m:
                        info = {k: int(v) for k, v in m.groupdict().items()}
                        prefix = 'S{story_id:02}_C{ch_id:02}'.format(**info)
                        for j, challenge in enumerate(score['value']):
                            # challenges += [f'{prefix}_CH{j+1:05}']
                            challenges += [challenge['name']]

        return {
            "available": weeks,
            "completed": challenges
        }

    def get_progress(self):

        progress = {
            "sicurezza": 0,
            "salute": 0,
            "sostenibilita": 0,
            "risparmio": 0,
        }
        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if 'type' in metric and 'name' in metric:
                    if metric['id'] == 'sicurezza_percentuale':
                        progress['sicurezza'] = int(score['value'])/100
                    if metric['id'] == 'salute_percentuale':
                        progress['salute'] = int(score['value'])/100
                    if metric['id'] == 'sostenibilita_percentuale':
                        progress['sostenibilita'] = int(score['value'])/100
                    if metric['id'] == 'risparmio_percentuale':
                        progress['risparmio'] = int(score['value'])/100

        return progress

    @property
    def json(self):
        return self.response



    # e = r['events']['local'][0]
    #
    # if e['changes'] and isinstance(e['changes'], list):
    #     for change in e['changes']:
    #         if change['metric']['type'] == 'point':
    #             status[change['metric']['name']] = change['delta']['new']
    #         elif change['metric']['type'] == 'set':
    #             completed_challenges.append(change['delta'])
