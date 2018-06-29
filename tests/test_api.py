import json
from unittest import TestCase
from gamecontroller import mapping
import requests
import json
import jsonschema
from jsonschema import  validate,  ValidationError

class ApiTest(TestCase):
    prod_endpoint = 'https://xz4740jwrg.execute-api.eu-west-1.amazonaws.com/prod/api'
    dev_endpoint = 'https://xz4740jwrg.execute-api.eu-west-1.amazonaws.com/dev/api'



        #json_playoff = json.load(open('get_user.json'))
        #self.json_response = json.load(open('get_user_response.json'))
        #
        # self.after = mapping.Mapping(
        #     self.json_playoff, weeks=52, ranking=0.25).json['body']
    def test_play_action_is_online(self):
        response = requests.post(
            url=f"{self.prod_endpoint}/play",
        )
        self.assertIsNotNone(response.status_code)

    def test_userupgrade_is_online(self):
        response = requests.post(
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
            url=f"{self.prod_endpoint}/userstatus?player=giovanni",
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

    def test_play(self):
        with open('./play_input.json', 'r') as f:
            input = f.read()

        data = json.loads(input)

        response = requests.post(
            url=f"{self.prod_endpoint}/play",
            data = data
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


    def test_userupgrade(self):
        with open('./userupgrade_input.json', 'r') as f:
            input = f.read()

        data = json.loads(input)

        response = requests.put(
            url=f"{self.prod_endpoint}/play",
            data=data
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




