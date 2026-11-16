# Weather Assistant — Implementation Plan

**Status:** Proposed
**Approach:** Outside-in TDD

## 1. Implementation Strategy

Implement the application through vertical functional slices.

Each slice starts with an externally observable behavior and introduces internal components only when required.

## 2. API Contract

| Method | Endpoint | Responsibility |
|---|---|---|
| POST | /messages | Generate a weather recommendation |
| GET | /weather | Retrieve weather information |
| GET | /conversations/{id}/messages | Retrieve conversation history |

### POST /messages

Request:

```json
{
  "conversation_id": null,
  "city": "Montreal",
  "message": "Is tomorrow suitable for running?",
  "mode": "ai"
}
```

Response (HTTP 200, illustrative data):

```json
{
  "conversation_id": "conv-001",
  "weather": {
    "city": "Montreal",
    "temperature": 5,
    "rain_probability": 80
  },
  "answer": "Indoor running is recommended."
}
```

## 3. Implementation Sequence

### Slice 1 — AI-Powered Recommendation

- Write a failing REST acceptance test.
- Implement the POST /messages endpoint.
- Introduce the recommendation use case.
- Retrieve weather information through a weather provider.
- Assemble the model context.
- Execute inference through Orvexa.
- Return weather information and the generated recommendation.
- Verify the acceptance test.

### Slice 2 — Local Mode

- Write a Local Mode acceptance test.
- Implement rule-based recommendation.
- Support mode selection.
- Verify that Local Mode does not invoke the model.

### Slice 3 — Multi-Turn Conversation

- Write conversation acceptance tests.
- Introduce conversation identity.
- Persist successful interactions using SQLite.
- Retrieve previous messages.
- Include relevant history in the model context.
- Verify conversation isolation.

### Slice 4 — Supporting Endpoints and Error Handling

- Expose weather information.
- Expose conversation history.
- Complete validation and failure scenarios.
- Verify external service integration.
- Document and demonstrate the API using Thunder Client.

## 4. Quality Gates

- pytest passes.
- Ruff checks pass.
- Pyright checks pass.
- Required REST endpoints are documented.
- Thunder Client demonstrates successful and erroneous requests.
