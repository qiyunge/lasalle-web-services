import json

from unittest.mock import Mock
from lab_intelligence.adapters.llm_generator import LLMRecommendationGenerator

def test_generate_recommendation():
    weather_data = {
        "city": "Montreal",
        "temperature": 5,
        "rain_probability": 80,
    }
    
    message = "Is it suitable for running today?"
    answer = "Indoor running is recommended."
    
    client = Mock()
    client.chat.completions.create.return_value = client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(message=Mock(content=answer))
        ]
    )
    generator = LLMRecommendationGenerator(client, model="qwen-1.5b")
    result = generator.generate(weather_data, message)
    assert result == answer
    
    client.chat.completions.create.assert_called_once()
    
    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "qwen-1.5b"
    messages = kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert json.dumps(weather_data) in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert message in messages[1]["content"]