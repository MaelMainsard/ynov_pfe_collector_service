import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_payload_validity

def test_payload_empty_string():
    assert check_payload_validity(b"") == False

def test_payload_invalid_json():
    assert check_payload_validity(b"This is not json") == True

def test_payload_not_list():
    assert check_payload_validity(b'{"key": "value"}') == False

def test_payload_list_not_empty():
    assert check_payload_validity(b'[]') == False

def test_payload_list_not_dictionary():
    assert check_payload_validity(b'["Het",{}]') == False

def test_payload_dictionnary_missing_field():
    assert check_payload_validity(b'[{"air_temperature": 24.3}]') == False

def test_payload_malformed_json():
    assert check_payload_validity(b'[{"air_temperature": 24.3, "relative_humidity"}]') == False

def test_payload_list_valid():
    assert check_payload_validity(b'[{"air_temperature": 24.3, "relative_humidity": 65.2, "soil_moisture": 45.1, "rainfall": 0.0, "leaf_wetness_duration": 2.5, "timestamp": "2024-01-15T10:30:00Z"}]') == True