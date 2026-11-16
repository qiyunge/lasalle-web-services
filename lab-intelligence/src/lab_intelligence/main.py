import os

import httpx
from openai import OpenAI

from lab_intelligence.app import create_app
from lab_intelligence.application.recommend_weather import (
    RecommendWeather,
)
from lab_intelligence.adapters.open_meteo import (
    OpenMeteoWeatherProvider,
)
from lab_intelligence.adapters.llm_generator import (
    LLMRecommendationGenerator,
)
from lab_intelligence.adapters.local_generator import (
    LocalRecommendationGenerator,
)
from lab_intelligence.adapters.conversation_store import (
    SQLiteConversationStore,
)


weather_provider = OpenMeteoWeatherProvider(
    client=httpx.Client(timeout=10.0),
)

ai_generator = LLMRecommendationGenerator(
    client=OpenAI(
        base_url=os.getenv(
            "LLM_BASE_URL", "http://localhost:8000/v1"
        ),
        api_key=os.getenv("LLM_API_KEY", "EMPTY"),
        timeout=30.0,
    ),
    model=os.getenv("LLM_MODEL", "qwen-1.5b"),
)

local_recommendation_generator = LocalRecommendationGenerator()

conversation_store = SQLiteConversationStore()

recommend_weather = RecommendWeather(
    weather_provider=weather_provider,
    ai_generator=ai_generator,
    local_generator=local_recommendation_generator,
    conversation_store=conversation_store,
)

app = create_app(
    recommend_weather=recommend_weather,
    weather_provider=weather_provider,
    conversation_store=conversation_store,
)


def serve():
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    serve()