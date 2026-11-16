from typing import Protocol

from lab_intelligence.application.exceptions import (
    ConversationNotFoundError,
    InvalidInputError,
)


class WeatherProvider(Protocol):
    def get_weather(self, city: str) -> dict: ...


class RecommendationGenerator(Protocol):
    def generate(
        self,
        weather: dict,
        message: str,
        history: list[dict] | None = None,
    ) -> str: ...


class ConversationStore(Protocol):
    def create(self) -> str: ...

    def exists(self, conversation_id: str) -> bool: ...

    def get(self, conversation_id: str) -> list[dict]: ...

    def append(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None: ...


class RecommendWeather:
    def __init__(
        self,
        weather_provider: WeatherProvider,
        ai_generator: RecommendationGenerator,
        local_generator: RecommendationGenerator,
        conversation_store: ConversationStore,
    ):
        self.weather_provider = weather_provider
        self.generators = {
            "ai": ai_generator,
            "local": local_generator,
        }
        self.conversation_store = conversation_store

    def execute(
        self,
        city: str,
        message: str,
        mode: str,
        conversation_id: str | None = None,
    ) -> dict:
        if mode not in self.generators:
            raise InvalidInputError("Invalid mode")

        if conversation_id is not None:
            if not self.conversation_store.exists(conversation_id):
                raise ConversationNotFoundError(conversation_id)

            history = self.conversation_store.get(conversation_id)
        else:
            history = []

        weather = self.weather_provider.get_weather(city)

        generator = self.generators[mode]

        answer = generator.generate(
            weather=weather,
            message=message,
            history=history,
        )

        if conversation_id is None:
            conversation_id = self.conversation_store.create()

        self.conversation_store.append(
            conversation_id, "user", message
        )

        self.conversation_store.append(
            conversation_id, "assistant", answer
        )

        return {
            "conversation_id": conversation_id,
            "mode": mode,
            "weather": weather,
            "answer": answer,
        }