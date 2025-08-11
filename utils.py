from peewee import *
import os
from dotenv import load_dotenv
from constant import Constant
import json
from datetime import datetime

constant = Constant()
load_dotenv()

# -----------------------------------------------------------------------
# Cette fonction retourne l'object de connection à la base de donnée
# -----------------------------------------------------------------------
def get_database():
    return PostgresqlDatabase(
        os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PSW'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

# -----------------------------------------------------------------------
# Cette fonction permet de vérifier la validitée de la payload de retour
# -----------------------------------------------------------------------
def check_payload_validity(payload):
    try:
        field_required = ["air_temperature", "relative_humidity", "soil_moisture", "rainfall", "leaf_wetness_duration","timestamp"]
        json_payload = json.loads(payload.decode('utf-8').replace("'", '"'))

        if not isinstance(json_payload, list) or len(json_payload) == 0:
            return {'valid': False, 'error': constant.WRONG_JSON_OR_EMPTY_LIST}

        for item in json_payload:
            if not isinstance(item, dict):
                return {'valid': False, 'error': constant.ITEMS_NOT_DICT}
            for field in field_required:
                if field not in item:
                    return {'valid': False, 'error': f'{constant.MISSING_FIELD}: {field}'}

        return {'valid': True, 'data': json_payload}

    except Exception as e:
        return {'valid': False, 'error': str(e)}

# -----------------------------------------------------------------------
# Cette fonction permet de vérifier l'intégrité des métriques reçu
# -----------------------------------------------------------------------
def check_metrics(param,data):
    try:
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            return {'valid': False, 'error': f'{constant.INVALID_TIMESTAMP}: {data["timestamp"]}'}

        if not param.air_temperature_min <= data['air_temperature'] <= param.air_temperature_max:
            return {'valid': False, 'error': f"${constant.INVALID_AIR_TEMPERATURE} : {data['air_temperature']}"}

        if not param.relative_humidity_min <= data['relative_humidity'] <= param.relative_humidity_max:
            return {'valid': False, 'error': f"${constant.INVALID_RELATIVE_HUMIDITY} : {data['relative_humidity']}"}

        if not param.soil_moisture_min <= data['soil_moisture'] <= param.soil_moisture_max:
            return {'valid': False, 'error': f"${constant.INVALID_SOIL_MOISTURE} : {data['soil_moisture']}"}

        if not param.rainfall_min <= data['rainfall'] <= param.rainfall_max:
            return {'valid': False, 'error': f"${constant.INVALID_RAINFALL} : {data['rainfall']}"}

        if not param.leaf_wetness_duration_min <= data['leaf_wetness_duration'] <= param.leaf_wetness_duration_max:
            return {'valid': False, 'error': f"${constant.INVALID_LEAF_WETNESS_DURATION} : {data['leaf_wetness_duration']}"}

        return {'valid': True}
    except Exception as e:
        return {'valid': False, 'error': str(e)}
