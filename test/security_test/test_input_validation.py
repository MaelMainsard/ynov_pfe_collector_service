import sys
import os
import time
from datetime import datetime
import pytest
import json
import paho.mqtt.publish as publisher
from testcontainers.compose import DockerCompose
from peewee import PostgresqlDatabase
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Models


def log_on_failure(func):
    def wrapper(self, infrastructure):
        try:
            return func(self, infrastructure)
        except Exception as e:
            if "compose" in infrastructure:
                logs = infrastructure["compose"].get_logs("collector_service")
                print(f"\n=== LOGS DU SERVICE COLLECTOR ===")
                for log in logs:
                    print(log)
                print(f"=== FIN DES LOGS ===\n")
            raise e

    return wrapper

class TestInputValidation:

    @pytest.fixture(scope="class")
    def infrastructure(self):
        with DockerCompose(".", compose_file_name="docker-compose.yaml") as compose:
            db = PostgresqlDatabase(
                    database="grape_db",
                    user="local_user",
                    password="simplepassword123",
                    host=compose.get_service_host("postgres", 5432),
                    port=compose.get_service_port("postgres", 5432),
            )
            yield {
                "db":db,
                "mqtt_port": compose.get_service_port("orange_mock", 1883),
                "mqtt_host": compose.get_service_host("orange_mock", 1883),
                "compose": compose
            }

    @log_on_failure
    def test_sql_injection_block(self, infrastructure):
        db = infrastructure["db"]
        db.connect()
        models = Models(db)

        malicious_station_uid = "e69cb64d-92f4-4ff2-9982-16e16a42c5a8'; DROP TABLE stationdata; --"
        initial_count = models.StationData.select().count()

        publisher.single(
            topic=f"station/{malicious_station_uid}",
            hostname=infrastructure["mqtt_host"],
            port=infrastructure["mqtt_port"],
            payload=json.dumps([{
                "air_temperature": 25.5,
                "relative_humidity": 60.5,
                "soil_moisture": 45.6,
                "rainfall": 0.2,
                "leaf_wetness_duration": 12,
                "timestamp": str(datetime.now())+"; DROP TABLE stationdata;"
            }])
        )

        time.sleep(2)

        final_count = models.StationData.select().count()
        assert final_count == initial_count, "L'injection SQL à réussi."