from peewee import *
from utils import get_database
import datetime
import uuid

db = get_database()

class Station(Model):
    id = UUIDField(primary_key=True, null=False)
    name = CharField(null=True, default="CHANGE_IT")
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


class StationParams(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    station_id = ForeignKeyField(Station, backref='data')
    air_temperature_min = IntegerField(default=-40)
    air_temperature_max = IntegerField(default=50)
    relative_humidity_min = IntegerField(default=0)
    relative_humidity_max = IntegerField(default=100)
    rainfall_min = FloatField(default=0.0)
    rainfall_max = FloatField(default=500.0)
    leaf_wetness_duration_min = IntegerField(default=0)
    leaf_wetness_duration_max = IntegerField(default=24)

    class Meta:
        database = db