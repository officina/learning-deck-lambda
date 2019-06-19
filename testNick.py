from gamecontroller.dynamo_models import User, UserReady
import os


os.environ['DYNAMODB_USERS_INFO_TABLE'] ='users_info-qa'
os.environ['DYNAMODB_USERS_READY_INFO_TABLE'] = 'users_info_ready-qa'


import boto3
from boto3.dynamodb.conditions import Key,Attr
boto3.setup_default_session(profile_name='learningdeck-prod')
dynamodb = boto3.resource('dynamodb', region_name="eu-central-1")

# print(dynamodb.list_tables())

table = dynamodb.Table('users_info-prod')
video_id = 25
import time

# filter = {
#     ":fn":{"S":"Amazon DynamoDB#DynamoDB Thread 1"},
#     ":num":{"N":"3"}
# }

for n in range(0, 1):
    start = time. time()
    response = boto3.client('dynamodb', region_name="eu-central-1").describe_table(
        TableName='users_info-prod'
    )
    end = time. time()
    print(response['Table']['GlobalSecondaryIndexes'])
    index = [x for x in response['Table']['GlobalSecondaryIndexes'] if x['IndexName'] == 'date_last_play-index']
    print(index[0]['ItemCount'])
    print(end - start)


from pynamodb.models import Model
