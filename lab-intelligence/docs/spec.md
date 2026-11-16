# Weather Assistant — Feature Specification

**Status:** Draft  
**Version:** 0.1.0  
**Development Approach:** Outside-in TDD

## 1. Overview

Weather Assistant is an intelligent REST API that retrieves weather information from Open-Meteo, provides activity recommendations in Local Mode and AI Mode, and supports multi-turn conversations.

## 2. User Scenarios & Testing

### User Story 1 — Intelligent Weather Recommendation (P1)

As a user, I want to receive weather information and recommendations tailored to my questions so that I can plan my activities.

**Independent Test:** Submit a weather request in either operating mode and verify that the response contains weather information and a relevant recommendation.

#### Acceptance Scenarios

**US-001-A: AI-powered recommendation**

- Given weather information is available for Montreal
- And the AI service is available
- When the user asks whether the weather is suitable for running in AI Mode
- Then the API returns HTTP 200
- And the response contains weather information
- And the response contains an AI-generated recommendation based on that information

**US-001-B: Rule-based recommendation**

- Given the weather forecast indicates a high probability of rain
- When the user requests a recommendation in Local Mode
- Then the API returns HTTP 200
- And the response recommends indoor activities
- And no LLM is invoked

**US-001-C: Unknown city**

- Given the requested city cannot be resolved
- When the user submits a weather request
- Then the API returns HTTP 404
- And the response explains the error

**US-001-D: Invalid request**

- Given the request contains missing or invalid required information
- When the user submits the request
- Then the API returns HTTP 400
- And the response identifies the validation error

**US-001-E: External service unavailable**

- Given the required weather or AI service is unavailable
- When the user submits a valid request that requires that service
- Then the API returns HTTP 503
- And the response identifies the unavailable service

### User Story 2 — Multi-Turn Conversation (P1)

As a user, I want to continue an existing conversation so that I can ask follow-up questions without repeating previously provided information.

**Independent Test:** Submit two consecutive requests using the same conversation identifier and verify that the second response uses relevant information from the first interaction.

#### Acceptance Scenarios

**US-002-A: Start a conversation**

- Given no conversation identifier is provided
- When the user submits a valid weather request
- Then the system returns a unique conversation identifier
- And the user message and assistant response are stored

**US-002-B: Continue a conversation**

- Given an existing conversation about Montreal weather
- When the user asks a follow-up question using the same conversation identifier
- Then the system generates a response using relevant previous information
- And the new interaction is appended to the conversation

**US-002-C: Conversation isolation**

- Given two independent conversations exist
- When the user continues one conversation
- Then information from the other conversation does not affect the response

**US-002-D: Unknown conversation**

- Given the provided conversation identifier does not exist
- When the user attempts to continue the conversation
- Then the API returns HTTP 404

**US-002-E: Retrieve conversation history**

- Given a conversation contains previous interactions
- When the user requests its history
- Then the API returns HTTP 200
- And the messages are returned in chronological order

## 3. Functional Requirements

- **FR-001:** The system MUST retrieve weather information from Open-Meteo.
- **FR-002:** The system MUST support Local Mode and AI Mode.
- **FR-003:** Local Mode MUST generate recommendations without invoking an LLM.
- **FR-004:** AI Mode MUST generate recommendations based on retrieved weather information and the user's question.
- **FR-005:** The system MUST assign a unique identifier to each new conversation.
- **FR-006:** The system MUST persist successful conversation interactions.
- **FR-007:** The system MUST use relevant conversation history when processing follow-up requests.
- **FR-008:** The system MUST isolate individual conversations.
- **FR-009:** The system MUST support retrieval of conversation history.
- **FR-010:** The system MUST validate incoming requests and return appropriate HTTP error responses.
- **FR-011:** The system MUST expose at least three documented REST endpoints.

## 4. Edge Cases

- Missing or empty message.
- Unsupported operating mode.
- Missing location in a new conversation.
- Unknown or ambiguous city name.
- Malformed JSON.
- Unknown conversation identifier.
- External API timeout or invalid response.
- AI service timeout or invalid response.
- Conversation persistence failure.

## 5. Key Entities

- **Weather Information:** Weather conditions or forecasts for a location.
- **Recommendation:** A response based on weather information and user input.
- **Conversation:** An ongoing interaction identified by a unique identifier.
- **Message:** A user or assistant contribution to a conversation.

## 6. Success Criteria

- **SC-001:** Both operating modes provide weather recommendations.
- **SC-002:** Users can ask contextual follow-up questions.
- **SC-003:** Conversation histories remain isolated.
- **SC-004:** Invalid requests and service failures produce documented error responses.
- **SC-005:** All acceptance scenarios pass automated tests.
- **SC-006:** At least three REST endpoints are implemented and documented.
- **SC-007:** Normal and error scenarios are demonstrated using Thunder Client.
- **SC-008:** The application can be installed and executed using the provided documentation.

## 7. Implementation Constraints

- Python and Flask.
- Open-Meteo external API.
- Non-Gemini LLM.
- No credentials committed to source control.
- Source code, dependencies, README, and Thunder Client test evidence included in the submission.

## 8. Proposed Technical Decisions

| Area | Approach |
|---|---|
| REST Framework | Flask |
| Weather Provider | Open-Meteo |
| AI Runtime | Orvexa Agent Harness |
| Execution Strategy | Application-driven |
| Model Provider | vLLM |
| Conversation Persistence | SQLite |
| Package Management | uv |
| Testing | pytest |
| Linting and Formatting | Ruff |
| Static Type Checking | Pyright |

## 9. Out of Scope

- Autonomous tool calling.
- Multi-agent orchestration.
- Runtime checkpointing and recovery.
- Distributed persistence.
- User authentication.
