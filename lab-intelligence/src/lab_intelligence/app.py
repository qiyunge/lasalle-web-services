from flask import Flask, request

from lab_intelligence.application.exceptions import (
    CityNotFoundError,
    ConversationNotFoundError,
    ExternalServiceError,
    InvalidInputError,
)
from lab_intelligence.application.recommend_weather import (
    RecommendWeather,
    WeatherProvider,
    ConversationStore,
)


def create_app(
    recommend_weather: RecommendWeather,
    weather_provider: WeatherProvider,
    conversation_store: ConversationStore,
) -> Flask:
    app = Flask(__name__)

    @app.post("/messages")
    def create_message():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            raise InvalidInputError("Expected a JSON object")

        city = data.get("city")
        message = data.get("message")
        mode = data.get("mode", "ai")
        conversation_id = data.get("conversation_id")

        if not isinstance(city, str) or not city.strip():
            raise InvalidInputError("City is required")

        if not isinstance(message, str) or not message.strip():
            raise InvalidInputError("Message is required")

        if mode not in ("ai", "local"):
            raise InvalidInputError("Mode must be ai or local")

        if conversation_id is not None and (
            not isinstance(conversation_id, str)
            or not conversation_id.strip()
        ):
            raise InvalidInputError("Invalid conversation_id")

        result = recommend_weather.execute(
            city=city.strip(),
            message=message.strip(),
            mode=mode,
            conversation_id=conversation_id,
        )

        return result, 200

    @app.get("/weather")
    def get_weather():
        city = request.args.get("city", "").strip()

        if not city:
            raise InvalidInputError("City is required")

        return weather_provider.get_weather(city), 200

    @app.get("/conversations/<conversation_id>/messages")
    def get_history(conversation_id):
        if not conversation_store.exists(conversation_id):
            raise ConversationNotFoundError(conversation_id)

        return {
            "conversation_id": conversation_id,
            "messages": conversation_store.get(conversation_id),
        }, 200

    @app.errorhandler(InvalidInputError)
    def handle_invalid_input(error):
        return {"error": str(error)}, 400

    @app.errorhandler(CityNotFoundError)
    def handle_city_not_found(error):
        return {"error": f"City not found: {error}"}, 404

    @app.errorhandler(ConversationNotFoundError)
    def handle_conversation_not_found(error):
        return {"error": f"Conversation not found: {error}"}, 404

    @app.errorhandler(ExternalServiceError)
    def handle_external_service(error):
        return {"error": str(error)}, 503

    return app