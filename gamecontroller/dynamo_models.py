import os
import pytz
from datetime import datetime, timedelta
import json
from pynamodb.models import Model
from pynamodb import attributes
from pynamodb.attributes import UnicodeAttribute
import time

# Defaults are handy when testing iteractively
USERS_TABLE_NAME = os.environ.get('DYNAMODB_USERS_INFO_TABLE') or 'users_info-dev'
USERS_READY_TABLE_NAME = os.environ.get('DYNAMODB_USERS_READY_INFO_TABLE') or 'users_info_ready-dev'
TOKEN_TABLE_NAME = os.environ.get('DYNAMODB_TOKEN_TABLE') or 'playoff_token-dev'
REGION = os.environ.get('AWS_REGION') or 'eu-central-1'
PLAYOFF_PROFILE_CACHE_DURATION_IN_MINUTES = os.environ.get('PLAYOFF_PROFILE_CACHE_DURATION_IN_MINUTES') or '10'
PLAYOFF_RANKING_CACHE_DURATION_IN_MINUTES = os.environ.get('PLAYOFF_RANKING_CACHE_DURATION_IN_MINUTES') or '10'


class User(Model):

    class Meta:
        table_name = USERS_TABLE_NAME
        region = REGION

    user_id = attributes.UnicodeAttribute(hash_key=True)
    date_start = attributes.UTCDateTimeAttribute()
    date_last_play = attributes.UTCDateTimeAttribute(null=True)
    playoff_user_profile = UnicodeAttribute(null=True)
    playoff_user_profile_last_update = attributes.UTCDateTimeAttribute(null=True)
    playoff_user_ranking = UnicodeAttribute(null=True)
    playoff_user_ranking_last_update = attributes.UTCDateTimeAttribute(null=True)

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

    # include anche la logica di durata della cache
    def update_playoff_user_profile(self, playoff_client, force_update=False):

        delta_in_millis = int(PLAYOFF_PROFILE_CACHE_DURATION_IN_MINUTES) * 60
        try:
            last_update_in_millis = int(time.mktime(self.playoff_user_profile_last_update.timetuple()))
        except:
            last_update_in_millis = -1
        now_in_millis = int(time.mktime(datetime.now().astimezone(pytz.UTC).timetuple()))

        if not force_update and self.playoff_user_profile is not None and now_in_millis < last_update_in_millis + delta_in_millis:
            print("Playoff user PROFILE update not needed")
            return self
        else:
            print("Playoff user PROFILE update REQUIRED")
            result = playoff_client.get(route=f"/admin/players/{self.user_id}")
            self.playoff_user_profile = json.dumps(result)
            self.playoff_user_profile_last_update = datetime.now().astimezone(pytz.UTC)
            self.save()
            return self

    # include anche la logica di durata della cache
    def update_playoff_user_ranking(self, playoff_client, force_update=False):
        delta_in_millis = int(PLAYOFF_RANKING_CACHE_DURATION_IN_MINUTES) * 60
        try:
            last_update_in_millis = int(time.mktime(self.playoff_user_ranking_last_update.timetuple()))
        except:
            last_update_in_millis = -1
        now_in_millis = int(time.mktime(datetime.now().astimezone(pytz.UTC).timetuple()))

        if not force_update and self.playoff_user_profile is not None and now_in_millis < last_update_in_millis + delta_in_millis:
            print("Playoff user RANKING update not needed")
            return self
        else:
            print("Playoff user RANKING update REQUIRED")
            result = playoff_client.get(
                route="/runtime/leaderboards/progressione_personale",
                query={
                    "player_id": self.user_id,
                    "cycle": "alltime",
                    "entity_id": self.user_id,
                    "radius": "0",
                    "sort": "descending",
                    "ranking": "relative"
                })
            self.playoff_user_ranking = json.dumps(result)
            self.playoff_user_ranking_last_update = datetime.now().astimezone(pytz.UTC)
            self.save()
            return self

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

    @property
    def playoff_user_profile_dict_format(self):
        if self.playoff_user_profile:
            return json.loads(self.playoff_user_profile)
        else:
            return None

    @property
    def playoff_user_profile_validity(self):
        if self.playoff_user_profile:
            return True
        else:
            return False

    @property
    def playoff_user_ranking_dict_format(self):
        if self.playoff_user_ranking:
            return json.loads(self.playoff_user_ranking)
        else:
            return None


class UserReady(Model):
    class Meta:
        table_name = USERS_READY_TABLE_NAME
        region = REGION

    user_id = attributes.UnicodeAttribute(hash_key=True)
    date_start = attributes.UTCDateTimeAttribute()
    date_last_play = attributes.UTCDateTimeAttribute(null=True)
    playoff_user_profile = UnicodeAttribute(null=True)
    playoff_user_profile_last_update = attributes.UTCDateTimeAttribute(null=True)
    playoff_user_ranking = UnicodeAttribute(null=True)
    playoff_user_ranking_last_update = attributes.UTCDateTimeAttribute(null=True)

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

    # include anche la logica di durata della cache
    def update_playoff_user_profile(self, playoff_client, force_update=False):

        delta_in_millis = int(PLAYOFF_PROFILE_CACHE_DURATION_IN_MINUTES) * 60
        try:
            last_update_in_millis = int(time.mktime(self.playoff_user_profile_last_update.timetuple()))
        except:
            last_update_in_millis = -1
        now_in_millis = int(time.mktime(datetime.now().astimezone(pytz.UTC).timetuple()))

        if not force_update and self.playoff_user_profile is not None and now_in_millis < last_update_in_millis + delta_in_millis:
            print("Playoff user PROFILE update not needed")
            return self
        else:
            print("Playoff user PROFILE update REQUIRED")
            result = playoff_client.get(route=f"/admin/players/{self.user_id}")
            self.playoff_user_profile = json.dumps(result)
            self.playoff_user_profile_last_update = datetime.now().astimezone(pytz.UTC)
            self.save()
            return self

    # include anche la logica di durata della cache
    def update_playoff_user_ranking(self, playoff_client, force_update=False):
        delta_in_millis = int(PLAYOFF_RANKING_CACHE_DURATION_IN_MINUTES) * 60
        try:
            last_update_in_millis = int(time.mktime(self.playoff_user_ranking_last_update.timetuple()))
        except:
            last_update_in_millis = -1
        now_in_millis = int(time.mktime(datetime.now().astimezone(pytz.UTC).timetuple()))

        if not force_update and self.playoff_user_profile is not None and now_in_millis < last_update_in_millis + delta_in_millis:
            print("Playoff user RANKING update not needed")
            return self
        else:
            print("Playoff user RANKING update REQUIRED")
            result = playoff_client.get(
                route="/runtime/leaderboards/progressione_personale",
                query={
                    "player_id": self.user_id,
                    "cycle": "alltime",
                    "entity_id": self.user_id,
                    "radius": "0",
                    "sort": "descending",
                    "ranking": "relative"
                })
            self.playoff_user_ranking = json.dumps(result)
            self.playoff_user_ranking_last_update = datetime.now().astimezone(pytz.UTC)
            self.save()
            return self

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

    @property
    def playoff_user_profile_dict_format(self):
        if self.playoff_user_profile:
            return json.loads(self.playoff_user_profile)
        else:
            return None

    @property
    def playoff_user_profile_validity(self):
        if self.playoff_user_profile:
            return True
        else:
            return False

    @property
    def playoff_user_ranking_dict_format(self):
        if self.playoff_user_ranking:
            return json.loads(self.playoff_user_ranking)
        else:
            return None

class Token(Model):

    class Meta:
        table_name = TOKEN_TABLE_NAME
        region = REGION

    token = attributes.UnicodeAttribute(hash_key=True)
    access_token = attributes.UnicodeAttribute()
    token_type = attributes.UnicodeAttribute()
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
