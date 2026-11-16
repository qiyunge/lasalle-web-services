class LocalRecommendationGenerator:
    def generate(self, weather: dict, message: str) -> str:
        temperature = weather["temperature"]
        rain_probability = weather["rain_probability"]

        recommendations = []

        if temperature < 0:
            recommendations.append("Wear warm winter clothing.")
        elif temperature < 10:
            recommendations.append("Wear a warm jacket.")
        elif temperature > 30:
            recommendations.append("Stay hydrated and avoid extreme heat.")
        else:
            recommendations.append("The temperature is comfortable.")

        if rain_probability >= 70:
            recommendations.append(
                "Rain is likely. Consider indoor activities."
            )
        elif rain_probability >= 30:
            recommendations.append("Bring an umbrella.")
        else:
            recommendations.append("Outdoor activities are recommended.")

        return " ".join(recommendations)