from models import Station, StationData
from utils import get_database, check_payload_validity
import os
import json
from dotenv import load_dotenv
import paho.mqtt.subscribe as subscribe
from datetime import datetime
from loguru import logger

load_dotenv()

logger.info("Starting script")
#--------------------------------------------------------
# Vérification de la présence des variables environements
#--------------------------------------------------------
required_env_vars = ['DB_NAME', 'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PSW', 'BRK_HOST', 'BRK_PORT', 'BRK_USER','BRK_PSW','ENV']

for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Missing {var} environment variable")
        exit(1)

#---------------------------------------------------------
# Script principal
#---------------------------------------------------------
try :
    #-----------------------------------------------------
    # Connection à la base de donnée
    #-----------------------------------------------------
    logger.info("Trying to connect to database")
    db = get_database()
    db.connect()
    db.create_tables([Station, StationData]) # On créez les tables si elles n'existe pas
    logger.info("Connected to database")

    while True:
        #--------------------------------------------------
        # Connection au broker MQTT
        #--------------------------------------------------
        logger.info("Waiting for station data.")
        msg = subscribe.simple(
            topics="station/#",
            hostname=os.getenv('BRK_HOST'),
            port=int(os.getenv('BRK_PORT')),
            auth={
                'username': os.getenv('BRK_USER'),
                'password': os.getenv('BRK_PSW')
            }
        )
        topic_parts = msg.topic.split('/')
        station_id = topic_parts[1]

        #--------------------------------------------------
        # Reception d'un nouveau message
        #--------------------------------------------------
        logger.info(f"New message received from station {station_id}")
        station = Station.get_or_create(id=station_id)

        # --------------------------------------------------
        # Récupération de la payload
        # --------------------------------------------------
        if check_payload_validity(msg.payload) and os.getenv('ENV') == station.env:

            data_array = json.loads(msg.payload.decode('utf-8').replace("'", '"'))

            # --------------------------------------------------
            # Enregistrement des métriques en bases
            # --------------------------------------------------
            for data in data_array:
                measured_datetime = datetime.fromtimestamp(data['timestamp'])

                StationData.create(
                    station_id=station_id,
                    air_temperature=data['air_temperature'],
                    relative_humidity=data['relative_humidity'],
                    rainfall=data['rainfall'],
                    leaf_wetness_duration=data['leaf_wetness_duration'],
                    measured_at=measured_datetime
                )

except Exception as e:
    logger.critical(f"An error appear : {e}")
    exit(1)






