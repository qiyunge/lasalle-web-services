from unittest.mock import Mock

from lab_intelligence.application.recommend_weather import RecommendWeather

def test_ai_recommendation():
    # Arrange
    weather_data = {
        "city": "Montreal",
        "temperature": 20,
        "rain_probability": 80
        
    }
    
    message = "Is tomorrow suitable for running?"
    answer = "Yes, tomorrow is suitable for running."
    
    weather_provider = Mock()
    weather_provider.get_weather.return_value = weather_data
    
    generator = Mock()
    generator.generate.return_value = answer
    
    use_case = RecommendWeather(weather_provider = weather_provider, generator = generator)
    
    # Act
    result = use_case.execute(city="Montreal", message=message, mode="ai")
    
    # Assert
    assert result == {
        "weather": weather_data,
        "answer": answer
    }
    
    weather_provider.get_weather.assert_called_once_with("Montreal")
    generator.generate.assert_called_once_with(weather_data, message)