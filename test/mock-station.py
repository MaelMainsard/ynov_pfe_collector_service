from datetime import datetime
import click
from loguru import logger
from dotenv import load_dotenv
import paho.mqtt.publish as publisher
import os
import json

load_dotenv()

@click.command()
@click.option("--station_uid", required=True)
@click.option("--air_temperature", required=True)
@click.option("--relative_humidity", required=True)
@click.option("--soil_moisture", required=True)
@click.option("--rainfall", required=True)
@click.option("--leaf_wetness_duration", required=True)
def send_prompt_data(station_uid,air_temperature,relative_humidity,soil_moisture,rainfall,leaf_wetness_duration):
    try :
        publisher.single(
            topic=f"station/{station_uid}",
            hostname="127.0.0.1",
            port=1883,
            payload=json.dumps([{
                "air_temperature": air_temperature,
                "relative_humidity": relative_humidity,
                "soil_moisture": soil_moisture,
                "rainfall": rainfall,
                "leaf_wetness_duration": leaf_wetness_duration,
                "timestamp": str(datetime.now())
            }])
        )
        logger.info("Données envoyées.")
    except Exception as e:
        logger.critical(f"An error appear : {e}")
        exit(1)

if __name__ == '__main__':
    send_prompt_data()