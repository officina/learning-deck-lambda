import boto3

client = boto3.client('dynamodb',aws_access_key_id='AKIAI3QR7GDF6FEB6R6Q',
    aws_secret_access_key='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', region='eu-west-1')
print(client.list_tables())