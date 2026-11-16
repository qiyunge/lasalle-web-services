def test_ai_weather_recommendation(client):
    request = {
        "conversation_id": None,
        "city": "Montreal",
        "message": " Is tomorrow suitable for running ?",
        "mode": "ai",
    }
    # Act
    response = client.post("/messages", json=request)

    assert response.status_code == 200

    data = response.json

    assert data["weather"]["city"] == "Montreal"
    assert data["answer"] is not None
