import httpx

from lab_intelligence.application.exceptions import (
    CityNotFoundError,
    ExternalServiceError,
)


class OpenMeteoWeatherProvider:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_weather(self, city: str) -> dict:
        try:
            response = self.client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1},
            )
            response.raise_for_status()

            locations = response.json().get("results", [])

            if not locations:
                raise CityNotFoundError(city)

            location = locations[0]

            response = self.client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "temperature_2m",
                    "daily": "precipitation_probability_max",
                    "forecast_days": 1,
                    "timezone": "auto",
                },
            )
            response.raise_for_status()

            data = response.json()

            return {
                "city": city,
                "temperature": data["current"]["temperature_2m"],
                "rain_probability": data["daily"][
                    "precipitation_probability_max"
                ][0],
            }

        except httpx.HTTPError as exc:
            raise ExternalServiceError(
                "Weather service unavailable"
            ) from exc

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError(
                "Invalid weather service response"
            ) from exc