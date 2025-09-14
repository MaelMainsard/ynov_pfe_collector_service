from peewee import *
import os
from dotenv import load_dotenv
from constant import Constant
import json
from datetime import datetime
from mailjet_rest import Client

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
        field_required = ["air_temperature", "relative_humidity", "soil_moisture", "rainfall", "solar_irradiance", "leaf_wetness_duration","timestamp"]
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
        errors_array = []
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            errors_array.append({'field': 'timestamp', 'value': data['timestamp']})

        if not param.air_temperature_min <= float(data['air_temperature']) <= param.air_temperature_max:
            errors_array.append({'field': 'air_temperature', 'value': data['air_temperature']})

        if not param.relative_humidity_min <= float(data['relative_humidity']) <= param.relative_humidity_max:
            errors_array.append({'field': 'relative_humidity', 'value': data['relative_humidity']})

        if not param.soil_moisture_min <= float(data['soil_moisture']) <= param.soil_moisture_max:
            errors_array.append({'field': 'soil_moisture', 'value': data['soil_moisture']})

        if not param.rainfall_min <= float(data['rainfall']) <= param.rainfall_max:
            errors_array.append({'field': 'rainfall', 'value': data['rainfall']})

        if not param.solar_irradiance_min <= float(data['solar_irradiance']) <= param.solar_irradiance_max:
            errors_array.append({'field': 'solar_irradiance','value': data['solar_irradiance']})

        if not param.leaf_wetness_duration_min <= float(data['leaf_wetness_duration']) <= param.leaf_wetness_duration_max:
            errors_array.append({'field': 'leaf_wetness_duration', 'value': data['leaf_wetness_duration']})

        if len(errors_array) > 0:
            return {'valid': False, 'errors': errors_array}
        else:
            return {'valid': True}

    except Exception as e:
        return {'valid': False, 'error': str(e)}

# -----------------------------------------------------------------------
# Cette fonction permet d'envoyer un email d'alerte
# -----------------------------------------------------------------------
def send_alert_email(station_name,threshold_limit,aberrant_metrics):
    try:
        mailjet = Client(
            auth=(
                os.getenv('MJ_APIKEY_PUBLIC'),
                os.getenv('MJ_APIKEY_PRIVATE')
            ),
            version='v3.1'
        )

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": os.getenv('ALERTING_EMAIL'),
                    },
                    "To": [
                        {
                            "Email": os.getenv('ALERTING_EMAIL'),
                        }
                    ],
                    "TemplateID": 7307492,
                    "TemplateLanguage": True,
                    "Variables": {
                        "STATION" : station_name,
                        "THRESHOLD": threshold_limit,
                        "ABERRANT_VALUES": aberrant_metrics
                    }
                }
            ]
        }
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            return {'success': True}
        else:
            return {'success': False, 'error': result.json()}

    except Exception as e:
        return {'success': False, 'error': str(e)}
