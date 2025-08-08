import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_payload_validity

def test_payload_empty_string():
    assert check_payload_validity(b"") == False

def test_payload_invalid_json():
    assert check_payload_validity(b"This is not json") == False

def test_payload_env_not_exist():
    assert check_payload_validity(b'{"env": , "data": [{"air_temperature": 24.3, "relative_humidity": 65.2, "soil_moisture": 45.1, "rainfall": 0.0, "leaf_wetness_duration": 2.5, "timestamp": "2024-01-15T10:30:00Z"}] }') == False

def test_payload_env_wrong():
    assert check_payload_validity(b'{"env": "startup", "data": [{"air_temperature": 24.3, "relative_humidity": 65.2, "soil_moisture": 45.1, "rainfall": 0.0, "leaf_wetness_duration": 2.5, "timestamp": "2024-01-15T10:30:00Z"}] }') == False

def test_payload_data_not_list():
    assert check_payload_validity(b'{"env": "startup", "data": {"air_temperature": 24.3, "relative_humidity": 65.2, "soil_moisture": 45.1, "rainfall": 0.0, "leaf_wetness_duration": 2.5, "timestamp": "2024-01-15T10:30:00Z"}}') == False

def test_payload_data_missing_field():
    assert check_payload_validity(b'{"env": "startup", "data": [{"air_temperature": 24.3}] }') == False

def test_payload_malformed_json():
    assert check_payload_validity(b'{"env": "startup", "data": [{"air_temperature"}] }') == False

def test_payload_list_valid():
    assert check_payload_validity(b'{"env": "dev", "data": [{"air_temperature": 24.3, "relative_humidity": 65.2, "soil_moisture": 45.1, "rainfall": 0.0, "leaf_wetness_duration": 2.5, "timestamp": "2024-01-15T10:30:00Z"}] }') == True