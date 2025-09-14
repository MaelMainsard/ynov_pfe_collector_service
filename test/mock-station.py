from datetime import datetime, timedelta
import click
import faker
from loguru import logger
from dotenv import load_dotenv
from faker import Faker
import paho.mqtt.publish as publisher
import json
import os

load_dotenv()

@click.group()
def cli():
    pass

@cli.command()
@click.option("--station_uid", required=True)
@click.option("--air_temperature", required=True)
@click.option("--relative_humidity", required=True)
@click.option("--soil_moisture", required=True)
@click.option("--rainfall", required=True)
@click.option("--solar_irradiance", required=True)
@click.option("--leaf_wetness_duration", required=True)
def send_prompt_data(station_uid,air_temperature,relative_humidity,soil_moisture,rainfall,solar_irradiance,leaf_wetness_duration):
    try :
        publisher.single(
            topic=f"station/{station_uid}",
            hostname=os.getenv('BRK_HOST'),
            port=int(os.getenv('BRK_PORT')),
            auth={"username":os.getenv('BRK_USER'), "password":os.getenv('BRK_PSW')},
            payload=json.dumps([{
                "air_temperature": air_temperature,
                "relative_humidity": relative_humidity,
                "soil_moisture": soil_moisture,
                "rainfall": rainfall,
                "solar_irradiance": solar_irradiance,
                "leaf_wetness_duration": leaf_wetness_duration,
                "timestamp": str(datetime.now())
            }])
        )
        logger.info(f"Données envoyées.")
    except Exception as e:
        logger.critical(f"An error appear : {e}")
        exit(1)

@cli.command()
@click.option("--station_uid", required=True)
@click.option("--nbr", type=int, required=True)
def create_mock_data(station_uid,nbr):
    try:
        faker = Faker()
        date_now = datetime.now()
        metrics_array = []
        for nb in range(nbr):
            metrics_array.append({
                "air_temperature": faker.random_int(-5, 40, 1),
                "relative_humidity": faker.random_int(0, 100, 1),
                "soil_moisture": faker.random_int(0, 100, 1),
                "rainfall": faker.random_int(0, 500, 1),
                "solar_irradiance": faker.random_int(0, 1361, 1),
                "leaf_wetness_duration": faker.random_int(0, 24, 1),
                "timestamp": str(date_now - timedelta(minutes=30 * nb))
            })

        publisher.single(
            topic=f"station/{station_uid}",
            hostname=os.getenv('BRK_HOST'),
            port=int(os.getenv('BRK_PORT')),
            auth={"username": os.getenv('BRK_USER'), "password": os.getenv('BRK_PSW')},
            payload=json.dumps(metrics_array)
        )

        logger.info("Données envoyées.")
    except Exception as e:
        logger.critical(f"An error appear : {e}")
        exit(1)

if __name__ == '__main__':
    cli()
