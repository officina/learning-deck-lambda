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

existing_tables = dynamo_db_client.list_tables()['TableNames']
print(existing_tables)

