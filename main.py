import sys
from datetime import datetime
from dateutil import parser
from models import Models
from utils import get_database, check_payload_validity, check_metrics, send_alert_email
import os
import json
from dotenv import load_dotenv
import paho.mqtt.subscribe as subscribe

from loguru import logger

load_dotenv()
logger.remove()
logger.add(sys.stdout, level="DEBUG")

logger.debug("Starting script")
#--------------------------------------------------------
# Vérification de la présence des variables environements
#--------------------------------------------------------
logger.debug("Checking environment variables")
required_env_vars = ['DB_NAME', 'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PSW', 'BRK_HOST', 'BRK_PORT', 'BRK_USER','BRK_PSW', 'ALERTING_EMAIL', 'MJ_APIKEY_PUBLIC', 'MJ_APIKEY_PRIVATE']

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
    db = get_database()
    models = Models(db)
    db.connect()
    db.create_tables([models.Station, models.StationData, models.StationParams, models.AberrantMetric]) # On créez les tables si elles n'existe pas
    logger.info("Connected to database")

    while True:
        # --------------------------------------------------
        # Attente d'un message
        # --------------------------------------------------
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
        # --------------------------------------------------
        # Reception d'un nouveau message
        # --------------------------------------------------

        topic_parts = msg.topic.split('/')
        station_id = topic_parts[1]

        # --------------------------------------------------
        # Récupération + validation de la payload
        # --------------------------------------------------
        result = check_payload_validity(msg.payload)

        if result['valid']:

            # --------------------------------------------------
            # Enregistrement de la station si necessaire
            # --------------------------------------------------

            station, created = models.Station.get_or_create(id=station_id)
            logger.info(f"New message received from station {station.name}")
            logger.info(f"Station uid {station.id}")
            if created:
                logger.info(f"Station saved.")

            # ---------------------------------------------------------
            # Enregistrement des paramêtres de la station si necessaire
            # ---------------------------------------------------------
            param, created = models.StationParams.get_or_create(station_id=station_id)
            if created:
                logger.info(f"Station params saved.")

            # ---------------------------------------------------------
            # Pour chacune des métriques reçues
            # ---------------------------------------------------------
            metrics_count = len(result['data'])
            logger.info(f"Saving station metrics ({metrics_count}).")
            for item in result['data']:

                # ---------------------------------------------------------
                # Vérification des valeurs des données mesurées
                # ---------------------------------------------------------

                metrics = check_metrics(param,item)

                if metrics['valid']:
                    measured_datetime = parser.isoparse(item['timestamp'])

                    models.StationData.create(
                        station_id=station_id,
                        air_temperature=float(item['air_temperature']),
                        relative_humidity=float(item['relative_humidity']),
                        soil_moisture=float(item['soil_moisture']),
                        rainfall=float(item['rainfall']),
                        solar_irradiance=float(item['solar_irradiance']),
                        leaf_wetness_duration=float(item['leaf_wetness_duration']),
                        measured_at=measured_datetime
                    )
                else:
                    if metrics['errors']:

                        # ---------------------------------------------------------
                        # En cas de valeurs aberrantes détectées
                        # ---------------------------------------------------------

                        logger.warning(f"Aberrant metric(s) detected. Adding entry to buffer.")
                        logger.warning(f"Metrics - {str(metrics['errors'])}")

                        # Enregistrement en bases des valeurs
                        models.AberrantMetric.create(
                            station=station_id,
                            aberrant_metrics=str(metrics['errors']),
                            received_at=datetime.now()
                        )

                        logger.info(f"Buffer updated.")

                        # ---------------------------------------------------------
                        # Vérification du seuil d'alerte
                        # ---------------------------------------------------------

                        aberrant_metrics = models.AberrantMetric.select().where(station_id == station_id)
                        aberrant_metrics_count = aberrant_metrics.count()

                        # En cas de dépassement du seuil
                        if aberrant_metrics_count >= param.aberrant_metric_threshold:
                            logger.warning(f"Threshold exceeded ({aberrant_metrics_count} >= {param.aberrant_metric_threshold}). Triggering email alert.")                            # Sending email

                            # ---------------------------------------------------------
                            # Conversion des données JSON -> Text / Html
                            # ---------------------------------------------------------
                            aberrant_metrics_text = ""
                            for aberrant_metric in aberrant_metrics:
                                json_metric = json.loads(aberrant_metric.aberrant_metrics.replace("'", '"'))
                                for item in json_metric:
                                    field_name = item["field"]
                                    min_value = getattr(param, f"{field_name}_min")
                                    max_value = getattr(param, f"{field_name}_max")
                                    aberrant_metrics_text += f"{field_name} = {item['value']}. Settings: {min_value} <= X <= {max_value}<br>"
                                aberrant_metrics_text += "received_at : "+str(aberrant_metric.received_at)+"<br><br>"

                            # ---------------------------------------------------------
                            # Envoi de l'email d'alerte
                            # ---------------------------------------------------------
                            email_result = send_alert_email(station.name,param.aberrant_metric_threshold,aberrant_metrics_text)
                            if email_result['success']:
                                logger.info(f"Alert email sent.")
                                models.AberrantMetric.delete().where(station_id == station_id).execute()
                                logger.info(f"Buffer reset")
                            else:
                                logger.error(f"Alert email failed. Error : {email_result['error']}")
                        else:
                            logger.info(f"Threshold not reached, monitoring continues.")
                    else:
                        logger.error(f"A problem occurred during the metrics check : {result['error']}")

            logger.info(f"All done.")
        else:
            logger.error(f"A problem occurred with the payload received : {msg.payload} => {result['error']}")

except Exception as e:
    logger.critical(f"An error appear : {e}")
    exit(1)



