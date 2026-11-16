import json


SYSTEM_PROMPT = """
You are a weather assistant.
Provide practical recommendations based on the supplied weather data.
Do not invent weather information.
Temperature is measured in Celsius.
Rain probability represents today's maximum precipitation probability.
""".strip()


class OrvexaRecommendationGenerator:
    def __init__(self, runtime):
        self.runtime = runtime

    def generate(self, weather: dict, message: str) -> str:
        items = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "system",
                "content": f"Weather data:\n{json.dumps(weather)}",
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        return self.runtime.execute(items=items)