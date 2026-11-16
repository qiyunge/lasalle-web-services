from unittest.mock import Mock

import pytest
from lab_intelligence.app import create_app
from lab_intelligence.application.recommend_weather import RecommendWeather


@pytest.fixture
def weather_provider():
    provider = Mock()
    provider.get_weather.return_value = {
        "city": "Montreal",
        "temperature": 20,
        "rain_probability": 80
    }
    return provider

@pytest.fixture
def generator():
    gen = Mock()
    gen.generate.return_value = "Yes, tomorrow is suitable for running."
    return gen  

@pytest.fixture
def recommend_weather(weather_provider, generator):
    return RecommendWeather(weather_provider=weather_provider, generator=generator)

@pytest.fixture
def client(recommend_weather):
    app = create_app(recommend_weather)
    app.config["TESTING"] = True
    return app.test_client()