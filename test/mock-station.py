from datetime import datetime
import click
from loguru import logger
from dotenv import load_dotenv
import paho.mqtt.publish as publisher
import json

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
@click.option("--leaf_wetness_duration", required=True)
def send_prompt_data(station_uid,air_temperature,relative_humidity,soil_moisture,rainfall,leaf_wetness_duration):
    try :
        publisher.single(
            topic=f"station/{station_uid}",
            hostname="switchyard.proxy.rlwy.net",
            port=19828,
            auth={"username":"orange_mock", "password":"lyjb7oam5ismv4xxurb4sr0uhcmbjl9m"},
            payload=json.dumps([{
                "air_temperature": air_temperature,
                "relative_humidity": relative_humidity,
                "soil_moisture": soil_moisture,
                "rainfall": rainfall,
                "leaf_wetness_duration": leaf_wetness_duration,
                "timestamp": str(datetime.now())
            }])
        )
        logger.info(f"Données envoyées.")
    except Exception as e:
        logger.critical(f"An error appear : {e}")
        exit(1)

@cli.command()
@click.option("--json_file", required=True, type=click.Path(exists=True))
@click.option("--station_uid", required=True)
def send_from_json(json_file, station_uid):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        for dict in data:
            publisher.single(
                topic=f"station/{station_uid}",
                hostname="switchyard.proxy.rlwy.net",
                port=19828,
                auth={"username":"orange_mock", "password":"lyjb7oam5ismv4xxurb4sr0uhcmbjl9m"},
                payload=json.dumps([{
                    "air_temperature": dict['air_temperature'],
                    "relative_humidity": dict['relative_humidity'],
                    "soil_moisture": dict['soil_moisture'],
                    "rainfall": dict['rainfall'],
                    "leaf_wetness_duration": dict['leaf_wetness_duration'],
                    "timestamp": dict['timestamp']
                }])
            )
        logger.info("Données envoyées.")
    except Exception as e:
        logger.critical(f"An error appear : {e}")
        exit(1)

if __name__ == '__main__':
    cli()