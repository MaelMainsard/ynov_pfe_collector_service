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
        env_allowed = ["dev","test","prod"]
        json_payload = json.loads(payload.decode('utf-8').replace("'", '"'))
        env = json_payload['env']
        data = json_payload['data']

        if env not in env_allowed or len(data) == 0:
            return False

        for item in data:
            if not isinstance(item, dict):
                return False
            for field in field_required:
                if field not in item:
                    return False
        return {
            'valid': True,
            'env': env,
            'data': data
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }
