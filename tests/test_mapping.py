import json
from unittest import TestCase
from gamecontroller import mapping


class MappingTest(TestCase):
    json_playoff = json.load(open('get_user.json'))
    json_response = json.load(open('get_user_response.json'))

    @classmethod
    def setUp(self):
        self.after = mapping.Mapping(
            self.json_playoff, weeks=52, ranking=0.25).json['body']

    def test_world_status(self):
        # ok
        self.assertEqual(
            self.after['world']['status'],
            self.json_response['world']['status'])

    def test_world_points(self):
        # ok
        self.assertEqual(
            self.after['world']['points']['total'],
            self.json_response['world']['points']['total'])

    def test_world_available(self):
        # ok
        self.assertEqual(
            self.after['world']['points']['available'],
            self.json_response['world']['points']['available'])

    def test_world_upgrade(self):
        self.assertEqual(
            self.after['world']['points']['upgrade'],
            self.json_response['world']['points']['upgrade'])

    def test_challenges(self):
        # ok...
        self.assertEqual(
            self.after['challenges']['completed'],
            self.json_response['challenges']['completed'])

    def test_progress_ranking(self):
        # ok
        self.assertEqual(
            self.after['progress']['ranking'],
            self.json_response['progress']['ranking'])

    def test_progress_params(self):
        self.assertEqual(
            self.after['progress']['params'],
            self.json_response['progress']['params'])
