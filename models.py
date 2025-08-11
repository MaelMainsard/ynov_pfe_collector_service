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
    air_temperature = FloatField(null=False)
    relative_humidity = FloatField(null=False)
    soil_moisture = FloatField(null=False)
    rainfall = FloatField(null=False)
    leaf_wetness_duration = FloatField(null=False)
    measured_at = DateTimeField(null=False)

    class Meta:
        database = db


class StationParams(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    station_id = ForeignKeyField(Station, backref='data')
    air_temperature_min = FloatField(default=-40)
    air_temperature_max = FloatField(default=50)
    relative_humidity_min = FloatField(default=0)
    relative_humidity_max = FloatField(default=100)
    soil_moisture_min = FloatField(default=0)
    soil_moisture_max = FloatField(default=100)
    rainfall_min = FloatField(default=0.0)
    rainfall_max = FloatField(default=500.0)
    leaf_wetness_duration_min = FloatField(default=0)
    leaf_wetness_duration_max = FloatField(default=24)

    class Meta:
        database = db