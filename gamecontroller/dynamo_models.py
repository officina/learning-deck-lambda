import os
import pytz

from datetime import datetime, timedelta

from pynamodb.models import Model
from pynamodb import attributes
import time

# Defaults are handy when testing iteractively
USERS_TABLE_NAME = os.environ.get('DYNAMODB_USERS_INFO_TABLE') or 'users_info-dev'
USERS_READY_TABLE_NAME = os.environ.get('DYNAMODB_USERS_READY_INFO_TABLE') or 'users_info_ready-dev'
TOKEN_TABLE_NAME = os.environ.get('DYNAMODB_TOKEN_TABLE') or 'playoff_token-dev'
REGION = os.environ.get('AWS_REGION') or 'eu-central-1'


class User(Model):

    class Meta:
        table_name = USERS_TABLE_NAME
        region = REGION

    user_id = attributes.UnicodeAttribute(hash_key=True)
    date_start = attributes.UTCDateTimeAttribute()
    date_last_play = attributes.UTCDateTimeAttribute(null=True)

    @classmethod
    def get_lazy_users(cls, date=None, days=None, state="PUBLISHED"):
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
    def date_last_play_timestamp_format(self):
        print(f"date_last_play_timestamp_format on table {USERS_TABLE_NAME} and model User")
        if self.date_last_play:
            return int(time.mktime(self.date_last_play.timetuple()))
        else:
            return 0

    @property
    def unblocked_weeks(self):
        weeks = (datetime.now().astimezone(pytz.UTC) - self.date_start).days // 7
        return weeks + 1


class UserReady(Model):
    class Meta:
        table_name = USERS_READY_TABLE_NAME
        region = REGION

    user_id = attributes.UnicodeAttribute(hash_key=True)
    date_start = attributes.UTCDateTimeAttribute()
    date_last_play = attributes.UTCDateTimeAttribute(null=True)

    @classmethod
    def get_lazy_users(cls, date=None, days=None, state="PUBLISHED"):
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
    def date_last_play_timestamp_format(self):
        print(f"date_last_play_timestamp_format on table {USERS_READY_TABLE_NAME} and model UserReady")
        if self.date_last_play:
            return int(time.mktime(self.date_last_play.timetuple()))
        else:
            return 0

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
    def set_token_dynamo(cls, token, po_state):
        print(f"set_token_dynamo START with state {po_state}")
        print(token)
        cls(
            f"{TOKEN_TABLE_NAME}_{po_state}",
            access_token=token['access_token'],
            token_type=token['token_type'],
            expires_at=str(token['expires_at'])
        ).save()
        print("set_token_dynamo END")

    @classmethod
    def get_token_dynamo(cls, po_state):
        print(f"LAMBDA - get_token_dynamo START with state {po_state}")
        try:
            tk = list(cls.scan(cls.token == f"{TOKEN_TABLE_NAME}_{po_state}"))[0]
            print("LAMBDA - get_token_dynamo FINISHED")
            return tk and tk.attribute_values or None
        except:
            return None
