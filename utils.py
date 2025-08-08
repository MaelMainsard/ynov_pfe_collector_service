from peewee import *
import os
from dotenv import load_dotenv
import json
from loguru import logger

load_dotenv()

# ------------------------------------------------------------------
# Cette fonction retourne l'object de connection à la base de donnée
# ------------------------------------------------------------------
def get_database():
    return PostgresqlDatabase(
        os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PSW'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

# ------------------------------------------------------------------
# Cette fonction permet de vérifier la validitée de la payload de retour
# ------------------------------------------------------------------
def check_payload_validity(payload):
    try:
        field_required = ["air_temperature","relative_humidity","soil_moisture","rainfall","leaf_wetness_duration","timestamp"]
        json_payload = json.loads(payload.decode('utf-8').replace("'", '"'))
        if not isinstance(json_payload, list) or len(json_payload) == 0:
            return False
        for item in json_payload:
            if not isinstance(item, dict):
                return False
            for field in field_required:
                if field not in item:
                    return False
        return True
    except Exception as e:
        logger.error(f"Error appear while decoding the payload : {e}")
        return False
