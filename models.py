from peewee import *
from database import get_database
import datetime
import uuid

db = get_database()

class Station(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=True, default="CHANGE_IT")
    env = CharField(null=True, default="DEV")
    last_update = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

class StationData(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    station_id = ForeignKeyField(Station, backref='data')
    air_temperature = IntegerField(null=False)
    relative_humidity = IntegerField(null=False)
    rainfall = FloatField(null=False)
    leaf_wetness_duration = IntegerField(null=False)
    measured_at = DateTimeField(null=False)

    class Meta:
        database = db