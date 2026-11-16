import httpx
import pytest


from lab_intelligence.adapters.open_meteo import OpenMeteoWeatherProvider

@pytest.mark.integration
def test_get_real_weather():
    with httpx.Client(timeout=10.0) as client:
        provider = OpenMeteoWeatherProvider(client)
        weather = provider.get_weather("Montreal")
        
        assert weather["city"] == "Montreal"
        assert isinstance(weather["temperature"], (int, float))
        assert 0 <= weather["rain_probability"] <= 100