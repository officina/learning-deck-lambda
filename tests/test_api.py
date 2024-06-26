import json
from unittest import TestCase
from gamecontroller import mapping
import requests
import json
import jsonschema
from jsonschema import  validate,  ValidationError

class ApiTest(TestCase):
    # prod_endpoint = 'https://xz4740jwrg.execute-api.eu-west-1.amazonaws.com/prod/api'
    prod_endpoint = "https://cqj2wl89n9.execute-api.eu-central-1.amazonaws.com/dev/api"
    prod_endpoint_new ="https://2zmur5pbf1.execute-api.eu-central-1.amazonaws.com/prod/api"
    # qa_endpoint = 'https://7h4zux15wi.execute-api.eu-central-1.amazonaws.com/prod/api' #fix it
    dev_endpoint = 'https://cqj2wl89n9.execute-api.eu-central-1.amazonaws.com/dev/api'



        #json_playoff = json.load(open('get_user.json'))
        #self.json_response = json.load(open('get_user_response.json'))
        #
        # self.after = mapping.Mapping(
        #     self.json_playoff, weeks=52, ranking=0.25).json['body']
    def test_play_action_is_online(self):
        response = requests.patch(
            url=f"{self.prod_endpoint}/play",
        )
        self.assertIsNotNone(response.status_code)

    def test_userupgrade_is_online(self):
        response = requests.patch(
            url=f"{self.prod_endpoint}/userupgrade",
        )
        self.assertIsNotNone(response.status_code)

    def test_user_status_is_online(self):
        response = requests.get(
            url=f"{self.prod_endpoint}/userstatus",
        )
        self.assertIsNotNone(response.status_code)

    def test_user_status(self):
        response = requests.get(
            url=f"{self.prod_endpoint}/userstatus/lucia",
        )

        self.assertEqual(response.status_code, 200)

        try:
            with open('../schemas/userstatus_schema.json', 'r') as f:
                schema_data = f.read()

            schema = json.loads(schema_data)
            content = json.loads(response.content)
            jsonschema.validate(content, schema)
        except ValidationError as error:
            self.fail(f"Schema validation failed with error:\n {error}")

    def test_play_2(self):
        with open('./data/play_input_new.json', 'r') as f:
            input = f.read()

        data = json.loads(input)

        response = requests.put(url=f"{self.prod_endpoint_new}/play/player_23?state=READY", json=data)

        self.assertEqual(response.status_code, 200)

        try:
            with open('../schemas/userstatus_schema.json', 'r') as f:
                schema_data = f.read()

            schema = json.loads(schema_data)
            content = json.loads(response.content)
            print(content)
            jsonschema.validate(content, schema)
        except ValidationError as error:
            self.fail(f"Schema validation failed with error:\n {error}")

    def test_userupgrade(self):
        with open('./data/levelupgrade_input.json', 'r') as f:
            input = f.read()

        data = json.loads(input)

        print(data)

        response = requests.put(
            url=f"{self.prod_endpoint}/levelupgrade/lucia",
            json=data
        )



        self.assertEqual(response.status_code, 200)

        try:
            with open('../schemas/userstatus_schema.json', 'r') as f:
                schema_data = f.read()

            schema = json.loads(schema_data)
            content = json.loads(response.content)
            jsonschema.validate(content, schema)
        except ValidationError as error:
            self.fail(f"Schema validation failed with error:\n {error}")




