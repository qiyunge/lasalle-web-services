import json

from openai import OpenAI, OpenAIError

from lab_intelligence.application.exceptions import (
    ExternalServiceError,
)


SYSTEM_PROMPT = """
You are a weather assistant.
Provide practical recommendations based on the supplied weather data.
Do not invent weather information.
Temperature is measured in Celsius.
Rain probability represents today's maximum precipitation probability.
""".strip()


class LLMRecommendationGenerator:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def generate(
        self,
        weather: dict,
        message: str,
        history: list[dict] | None = None,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Weather data:\n{json.dumps(weather)}"
                ),
            },
            *(history or []),
            {
                "role": "user",
                "content": message,
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except OpenAIError as exc:
            raise ExternalServiceError(
                "LLM service unavailable"
            ) from exc

        answer = response.choices[0].message.content

        if not answer:
            raise ExternalServiceError("Empty LLM response")

        return answer