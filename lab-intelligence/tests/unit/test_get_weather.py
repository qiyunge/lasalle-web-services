import httpx

from lab_intelligence.adapters.open_meteo import OpenMeteoWeatherProvider

def test_get_weather():
    def handler(request: httpx.Request):
        if request.url.path == "/v1/search":
            return httpx.Response(
                status_code=200,
                json={
                    "results": [
                        {
                            "id": 6077243,
                            "city": "Montreal",
                            "latitude": 45.50884,
                            "longitude": -73.58781,
                            "elevation": 31.0,
                            "feature_code": "PPLA",
                            "country_code": "CA",
                            "admin1_id": 6077243,
                            "admin2_id": 0,
                            "timezone": "America/Toronto",
                            "population": 1704694,
                        }
                    ]
                },
            )
            
        if request.url.path == "/v1/forecast":
            return httpx.Response(
                status_code=200,
                json = {
                    "current":{
                        "temperature_2m": 5,
                    },
                    "daily": {
                        "precipitation_probability_max": [80]
                    },
                }
            )
            
        raise AssertionError(f"Unhandled request: {request.url}")
    
    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        provider = OpenMeteoWeatherProvider(client)
        weather = provider.get_weather("Montreal")
        
        assert weather["city"] == "Montreal"
        assert weather["temperature"] == 5
        assert weather["rain_probability"] == 80