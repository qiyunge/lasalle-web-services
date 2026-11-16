import logging

import pytest
from openai import OpenAI

from lab_intelligence.adapters.llm_generator import (
    LLMRecommendationGenerator,
)

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_generate_real_recommendation():
    weather = {
        "city": "Montreal",
        "temperature": 5,
        "rain_probability": 80,
    }

    message = "Is it suitable for running today?"

    with OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
        timeout=30.0,
    ) as client:
        generator = LLMRecommendationGenerator(
            client=client,
            model="qwen-1.5b",
        )

        answer = generator.generate( weather,message)

    logger.info("Weather: %s", weather)
    logger.info("Question: %s", message)
    logger.info("Answer: %s", answer)

    assert isinstance(answer, str)
    assert answer.strip()