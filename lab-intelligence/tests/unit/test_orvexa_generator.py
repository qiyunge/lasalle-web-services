import json

from unittest.mock import Mock

from lab_intelligence.adapters.orvexa_generator import OrvexaRecommendationGenerator

def test_generate_recommendation():
    
    weather_data = {
        "city": "Montreal",
        "temperature": 5,
        "rain_probability": 80,
    }
    
    message = "Is it suitable for running today?"
    answer = "Indoor running is recommended."
    
    runtime = Mock()
    runtime.execute.return_value = answer
    
    generator = OrvexaRecommendationGenerator(runtime)
    result = generator.generate(weather_data, message)
    assert result == answer
    
    runtime.execute.assert_called_once()
    items = runtime.execute.call_args[1]["items"]
    
    assert items[0]["role"] == "system"
    assert items[1]["role"] == "system"
    assert json.dumps(weather_data) in items[1]["content"]
    assert items[2]["role"] == "user"