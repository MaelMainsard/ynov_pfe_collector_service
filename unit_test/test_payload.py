import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_payload_validity

def test_payload_empty_string():
    result = check_payload_validity(b"")
    assert result['valid'] == False

def test_payload_invalid_json():
    result = check_payload_validity(b"This is not json")
    assert result['valid'] == False

def test_payload_not_list():
    result = check_payload_validity(b'{"key": "value"}')
    assert result['valid'] == False

def test_payload_list_not_empty():
    result = check_payload_validity(b'[]')
    assert result['valid'] == False

def test_payload_list_not_dictionary():
    result = check_payload_validity(b'["Het",{}]')
    assert result['valid'] == False

def test_payload_dictionnary_missing_field():
    result = check_payload_validity(b'[{"air_temperature": 24.3}]')
    assert result['valid'] == False

def test_payload_malformed_json():
    result = check_payload_validity(b'[{"air_temperature": 24.3, "relative_humidity"}]')
    assert result['valid'] == False

def test_payload_list_valid():
    result = check_payload_validity(b'[{"air_temperature": 24.3, "relative_humidity": 65.2, "soil_moisture": 45.1, "rainfall": 0.0, "leaf_wetness_duration": 2.5, "timestamp": "2024-01-15T10:30:00Z"}]')
    assert result['valid'] == True