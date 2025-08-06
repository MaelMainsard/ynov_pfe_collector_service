from models import Station, StationData
from database import get_database
import os
import json
from dotenv import load_dotenv
import paho.mqtt.subscribe as subscribe
from datetime import datetime
from loguru import logger

db = get_database()
load_dotenv()

if not os.getenv('DB_NAME'):
    logger.error("Missing DB_NAME environment variable")
if not os.getenv('DB_HOST'):
    logger.error("Missing DB_HOST environment variable")
if not os.getenv('DB_PORT'):
    logger.error("Missing DB_PORT environment variable")
if not os.getenv('DB_USER'):
    logger.error("Missing DB_USER environment variable")
if not os.getenv('DB_PSW'):
    logger.error("Missing DB_PSW environment variable")
if not os.getenv('BRK_HOST'):
    logger.error("Missing BRK_HOST environment variable")
if not os.getenv('BRK_PORT'):
    logger.error("Missing BRK_PORT environment variable")

def get_station(station_id):
    count = Station.select().where(Station.id == station_id).count()

    if count > 0:
        existing_station = Station.select().where(Station.id == station_id).get()
        existing_station.last_update = datetime.datetime.now()
        existing_station.save()
        return existing_station
    else:
        new_station = Station.create(id=station_id)
        return new_station

if __name__ == '__main__':
    logger.info("Starting script")
    db.connect()
    db.create_tables([Station, StationData])
    logger.info("Successfully connected to database")
    while True:
        logger.info("Waiting for stations datas.")
        msg = subscribe.simple(topics="station/#", hostname=os.getenv('BRK_HOST'), port=int(os.getenv('BRK_PORT')))

        topic_parts = msg.topic.split('/')
        station_id = topic_parts[1] if len(topic_parts) > 1 else None

        if not station_id:
            continue

        station = get_station(station_id)

        data_array = json.loads(msg.payload.decode('utf-8').replace("'", '"'))

        for data in data_array:
            measured_datetime = datetime.fromtimestamp(data['timestamp'])

            # noinspection PyPackageRequirements
            StationData.create(
                station_id=station_id,
                air_temperature=data['air_temperature'],
                relative_humidity=data['relative_humidity'],
                rainfall=data['rainfall'],
                leaf_wetness_duration=data['leaf_wetness_duration'],
                measured_at=measured_datetime
            )





