# coding: utf-8
"""
Implementazione del capitolo 6.3.1.1 Questa parte non necessita di aws

"""
import re
from datetime import datetime

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

BADGES_METRIC_ID='badges'

class Mapping:

    def __init__(self, result, weeks, ranking, date_last_play=0, date_start=-1):
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
        # self.response['body']['world']['available'] = available
        self.response['body']['world']['points']['upgrade'] = self.upgrade
        self.response['body']['challenges'] = self.get_challenges_grouped(weeks, date_start)
        self.response['body']['badges'] = self.get_badges()
        self.response['body']['progress']['params'] = self.get_progress()
        self.response['body']['progress']['ranking'] = ranking
        self.response['body']['timestamp'] = int(datetime.now().timestamp())
        self.response['body']['lastPlayed'] = date_last_play

    def get_status(self):

        map = {
            "livelli_asset_1": 'livelli_asset_1',
            "livelli_asset_2": 'livelli_asset_2',
            "livelli_asset_3": 'livelli_asset_3',
            "livelli_asset_4": 'livelli_asset_4'
        }

        status = {}
        self.upgrade = {}

        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if metric['id'].startswith('livelli_'):
                    value = int(score['value']['name'].replace('stato_', ''))
                    key = map[metric['id']]
                    # TODO: define a logic
                    label = metric['name'].replace('livelli ', '')
                    status[label] = value
                    hi = int(score['meta']['high'])
                    lw = int(score['meta']['low'])
                    print(f"Recap per {metric['id']}: hi={hi} lw={lw}")
                    self.upgrade[label] = (hi - lw + 1)

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

    def get_challenges_grouped(self, weeks, date_start):

        challenges = []
        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                chapter = {
                    "id": metric['id'],
                    "completed": []
                }
                if metric.get('type', None) == 'set' and metric.get('id', None) != BADGES_METRIC_ID:
                    for item in score['value']:
                        if int(item['count']) > 0:
                            chapter['completed'].append(item['name'])

                if len(chapter['completed']) > 0:
                    challenges.append(chapter)
        from datetime import datetime
        return {
            # "available": weeks,
            "start_date": int(datetime.timestamp(date_start)),
            "chapters": challenges
        }

    def get_badges(self):
        badges = []
        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if metric.get('type', None) == 'set' and metric.get('id', None) == BADGES_METRIC_ID:
                    for item in score['value']:
                        if int(item['count']) > 0:
                            badges.append(item['name'])

        return badges

    def get_progress(self):

        progress = {}
        temp_labels = {}
        # setup empty object
        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if 'type' in metric and 'name' in metric and metric['id'] == 'skill_1':
                    progress[metric['name']] = 0
                    temp_labels['skill_1'] = metric['name']
                if 'type' in metric and 'name' in metric and metric['id'] == 'skill_2':
                    progress[metric['name']] = 0
                    temp_labels['skill_2'] = metric['name']
                if 'type' in metric and 'name' in metric and metric['id'] == 'skill_3':
                    progress[metric['name']] = 0
                    temp_labels['skill_3'] = metric['name']
                if 'type' in metric and 'name' in metric and metric['id'] == 'skill_4':
                    progress[metric['name']] = 0
                    temp_labels['skill_4'] = metric['name']

        for score in self.result['scores']:
            if 'metric' in score and 'value' in score:
                metric = score['metric']
                if 'type' in metric and 'name' in metric:
                    if metric['id'] == 'skill_1_percentuale':
                        try:
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]] = int(score['value'])/100
                        except Exception as e:
                            print(e)
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]]
                    if metric['id'] == 'skill_2_percentuale':
                        try:
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]] = int(score['value']) / 100
                        except Exception as e:
                            print(e)
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]]
                    if metric['id'] == 'skill_3_percentuale':
                        try:
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]] = int(score['value']) / 100
                        except Exception as e:
                            print(e)
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]]
                    if metric['id'] == 'skill_4_percentuale':
                        try:
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]] = int(score['value']) / 100
                        except Exception as e:
                            print(e)
                            progress[temp_labels[metric['id'].replace('_percentuale', '')]]

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
