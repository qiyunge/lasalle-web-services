import logging

import pytest

from lab_intelligence.adapters.orvexa_generator import (
    OrvexaRecommendationGenerator,
)

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_generate_real_recommendation(runtime):
    # weather = {
    #     "city": "Montreal",
    #     "temperature": 5,
    #     "rain_probability": 80,
    # }

    # message = "Is it suitable for running today?"

    # generator = OrvexaRecommendationGenerator(runtime)

    # answer = generator.generate( weather, message)

    # logger.info("Weather: %s", weather)
    # logger.info("Question: %s", message)
    # logger.info("AI answer: %s", answer)

    # assert isinstance(answer, str)
    # assert answer.strip()
    pass