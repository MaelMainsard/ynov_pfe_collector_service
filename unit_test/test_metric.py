import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_metrics
from constant import Constant

constant = Constant()

class MockParam:
    def __init__(self):
        self.air_temperature_min = 10.0
        self.air_temperature_max = 40.0
        self.relative_humidity_min = 20.0
        self.relative_humidity_max = 100.0
        self.soil_moisture_min = 10.0
        self.soil_moisture_max = 100.0
        self.rainfall_min = 0.0
        self.rainfall_max = 50.0
        self.leaf_wetness_duration_min = 0.0
        self.leaf_wetness_duration_max = 24.0

def test_wrong_metric_timestamp():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 45.1,
        "rainfall": 0.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-150:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == False
    assert constant.INVALID_TIMESTAMP in result['error']

def test_good_metric_timestamp():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 45.1,
        "rainfall": 0.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == True

def test_wrong_relative_humidity():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 1326758,
        "soil_moisture": 45.1,
        "rainfall": 0.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == False
    assert constant.INVALID_RELATIVE_HUMIDITY in result['error']

def test_good_relative_humidity():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 45.1,
        "rainfall": 0.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == True

def test_wrong_soil_moisture():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 0,
        "rainfall": 0.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == False
    assert constant.INVALID_SOIL_MOISTURE in result['error']

def test_good_soil_moisture():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 45.1,
        "rainfall": 0.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == True

def test_wrong_rainfall():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 20.0,
        "rainfall": 60.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == False
    assert constant.INVALID_RAINFALL in result['error']

def test_good_rainfall():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 45.1,
        "rainfall": 20.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == True

def test_wrong_leaf_wetness_duration():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 20.4,
        "rainfall": 5.0,
        "leaf_wetness_duration": 60.0,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == False
    assert constant.INVALID_LEAF_WETNESS_DURATION in result['error']

def test_good_leaf_wetness_duration():
    mock_metric = MockParam()
    data = {
        "air_temperature": 24.3,
        "relative_humidity": 65.2,
        "soil_moisture": 45.1,
        "rainfall": 20.0,
        "leaf_wetness_duration": 2.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    result = check_metrics(mock_metric, data)
    assert result['valid'] == True