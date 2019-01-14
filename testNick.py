from gamecontroller.dynamo_models import User, UserReady
import os


os.environ['DYNAMODB_USERS_INFO_TABLE'] ='users_info-qa'
os.environ['DYNAMODB_USERS_READY_INFO_TABLE'] = 'users_info_ready-qa'


print(os.environ.get('DYNAMODB_USERS_INFO_TABLE'))

# user = UserReady('player_test_1').save()

# print(user)

print(UserReady.get('player_test_1').date_last_play_timestamp_format)
print(User.get('player_test_1').date_last_play_timestamp_format)
