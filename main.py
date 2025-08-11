from models import Station, StationData, StationParams
from utils import get_database, check_payload_validity, check_metrics
import os
from dotenv import load_dotenv
import paho.mqtt.subscribe as subscribe
from datetime import datetime
from loguru import logger

load_dotenv()

logger.info("Starting script")
#--------------------------------------------------------
# Vérification de la présence des variables environements
#--------------------------------------------------------
required_env_vars = ['DB_NAME', 'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PSW', 'BRK_HOST', 'BRK_PORT', 'BRK_USER','BRK_PSW']

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
    db.create_tables([Station, StationData, StationParams]) # On créez les tables si elles n'existe pas
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

        # --------------------------------------------------
        # Récupération de la payload
        # --------------------------------------------------
        result = check_payload_validity(msg.payload)

        if result['valid']:
            logger.info(f"Saving station if not exist.")
            station = Station.get_or_create(id=station_id)
            # --------------------------------------------------
            # Enregistrement des métriques en bases
            # --------------------------------------------------
            logger.info(f"Saving station data.")
            param = StationParams.get_or_create(station_id=station_id)
            for item in result['data']:

                metrics = check_metrics(param,item)

                if metrics['valid']:
                    measured_datetime = datetime.fromtimestamp(item['timestamp'])

                    StationData.create(
                        station_id=station_id,
                        air_temperature=item['air_temperature'],
                        relative_humidity=item['relative_humidity'],
                        rainfall=item['rainfall'],
                        leaf_wetness_duration=item['leaf_wetness_duration'],
                        measured_at=measured_datetime
                    )
                else:
                    logger.warning(f"Data was not saved. Cause : {metrics['error']}")
            logger.info(f"All done.")
        else:
            logger.error(f"A problem occurred with the payload received : {msg.payload} => {result['error']}")

except Exception as e:
    logger.critical(f"An error appear : {e}")
    exit(1)






