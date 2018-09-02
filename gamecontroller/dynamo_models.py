import os
import pytz

from datetime import datetime, timedelta

from pynamodb.models import Model
from pynamodb import attributes
from boto3.dynamodb.conditions import Key, Attr

# Defaults are handy when testing iteractively
USERS_TABLE_NAME = os.environ.get('DYNAMODB_USERS_INFO_TABLE') or 'users_info-dev'
TOKEN_TABLE_NAME = os.environ.get('DYNAMODB_TOKEN_TABLE') or 'playoff_token-dev'
REGION = os.environ.get('AWS_REGION') or 'eu-west-1'


class User(Model):

    class Meta:
        table_name = USERS_TABLE_NAME
        region = REGION

    user_id = attributes.UnicodeAttribute(hash_key=True)
    date_start = attributes.UTCDateTimeAttribute()
    date_last_play = attributes.UTCDateTimeAttribute(null=True)

    @classmethod
    def get_lazy_users(cls, date=None, days=None):
        date = (date or datetime.now()).astimezone(pytz.UTC)
        if days:
            date = date - timedelta(days=days)
        return cls.scan(cls.date_last_play <= date)

    def save(self, *args, **kwargs):
        if not self.date_start:
            self.date_start = datetime.now().astimezone(pytz.UTC)
        return super().save(*args, **kwargs)

    def save_last_play(self, now=None):
        self.date_last_play = (now or datetime.now()).astimezone(pytz.UTC)
        return self.save()

    @property
    def unblocked_weeks(self):
        weeks = (datetime.now().astimezone(pytz.UTC) - self.date_start).days // 7
        return weeks + 1


class Token(Model):

    class Meta:
        table_name = TOKEN_TABLE_NAME
        region = REGION

    token = attributes.UnicodeAttribute(hash_key=True)
    access_token = attributes.UnicodeAttribute()
    token_type = attributes.UnicodeAttribute()
    #expires_at = attributes.UTCDateTimeAttribute()
    expires_at = attributes.UnicodeAttribute()

    @classmethod
    def set_token_dynamo(cls, token):
        cls(
            TOKEN_TABLE_NAME,
            access_token=token['access_token'],
            token_type=token['token_type'],
            expires_at=str(token['expires_at'])
        ).save()

    @classmethod
    def get_token_dynamo(cls):
        tk = list(cls.scan(cls.token == TOKEN_TABLE_NAME))[0]
        return tk and tk.attribute_values or None
