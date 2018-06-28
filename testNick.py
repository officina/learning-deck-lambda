import boto3

client = boto3.client('dynamodb',aws_access_key_id='AKIAI3QR7GDF6FEB6R6Q',
    aws_secret_access_key='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', region='eu-west-1')
print(client.list_tables())


def get_playoff_client():
   return Playoff(
       client_id=CLIENT_ID,
       client_secret=CLIENT_SECRET,
       type="client",
       allow_unsecure=True,
       store=lambda token: Token.set_token_dynamo(token),
       load=lambda: Token.get_token_dynamo(),
   )


def get_user_status(event, context, player, playoff_client):

   result = playoff_client.get(route=f"/admin/players/{player}",)
   result_ranking = playoff_client.get(
       route=f"/runtime/leaderboards/progressione_personale?player_id={player}&cycle=alltime&entity_id={player}&radius=0&sort=descending&ranking=relative",)
  ...