# HTTP Contract: Student Self-Enrollment

Date: 2026-10-16

Business messages follow [spec.md](../spec.md). Stored fields follow
[data-model.md](../data-model.md). Technology choices follow
[research.md](../research.md).

A trusted caller context supplies the acting student. This service
does not authenticate that context. Callers send `acting_student_id`
on enrollment. The request does not accept a target student.

## Browse courses

`GET /courses`

No query parameters. No request body. No student identifier.

### Response

`200` with the set of existing courses. Each course includes its
identifier, course code, and name. A course that lacks a nonempty code
or a nonempty name is absent. The set includes courses outside the
student's programme and courses the student is already enrolled in.
The specification does not require an order. The current service
returns courses sorted by course code ascending. That order is
presentation, not a business rule.

When no existing course is stored, the status is still `200` and
`courses` is empty.

```json
{
  "courses": [
    {
      "id": 1,
      "course_code": "CS101",
      "name": "Introduction to Computer Science"
    }
  ]
}
```

## Enroll

`POST /inscriptions`

`Content-Type: application/json`

```json
{
  "acting_student_id": 1,
  "course_id": 10
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| acting_student_id | yes | Integer identifier of the acting student supplied by the trusted caller context. |
| course_id | yes | Integer identifier of the course to join. |
| student_id | not accepted | Not an enrollment field. A value that differs from `acting_student_id` names another student and is not supported. An equal value does not select a different student. The inscription student is always the acting student. |
| note | no | A present key, including JSON null, is a grade attempt. Omit the key for a successful enrollment. |

A body that is not a JSON object is read as an empty object.

The adapter maps this body to an application input contract. It does
not apply the business sentences.

### Input validation

These checks happen before a validated command exists. They are not
part of FR-014. Nothing is written.

The current service returns the first of these sentences:

| Condition | Status | `message` |
| --- | --- | --- |
| `acting_student_id` is missing | 400 | acting_student_id is required. |
| `course_id` is missing | 400 | course_id is required. |
| Either identifier is present and is not an integer, including a boolean | 400 | acting_student_id and course_id must be integers. |

The specification does not define these sentences. They are the
sentences the service already returns. One failure still uses the
matching row above.

The application result uses these stable codes and field names:

| Code | Field |
| --- | --- |
| `acting_student_id_missing` | `acting_student_id` |
| `course_id_missing` | `course_id` |
| `acting_student_id_not_integer` | `acting_student_id` |
| `course_id_not_integer` | `course_id` |

**Resolved (UD-001).** When more than one of these failures applies,
the response is HTTP 400. The body is a structured `errors` array.
Each element has the stable `code` and the `field` name. The array
lists `acting_student_id` before `course_id`. A field that is missing
is not also reported as not an integer.

```json
{
  "errors": [
    {
      "code": "acting_student_id_missing",
      "field": "acting_student_id"
    },
    {
      "code": "course_id_missing",
      "field": "course_id"
    }
  ]
}
```

A body that is not a JSON object is an empty object, so both required
identifiers are missing and this array is the response. This replaces
the earlier single sentence for that request. One failure still uses
the `message` row above. This response is input validation. It is not
a business refusal and it is not part of FR-014. When this validation
fails, the response does not also include a business sentence. FR-014
applies after the required identifiers pass validation.

### Created

`201`

```json
{
  "message": "You are enrolled in this course.",
  "inscription": {
    "id": 50,
    "student_id": 1,
    "course_id": 10,
    "note": null
  }
}
```

`student_id` is the acting student. `note` is null.

### Business refusals

Accepted FR-014: the first matching rule is the only message. The
attempt changes nothing.

| Order | Condition | Status | `message` |
| --- | --- | --- | --- |
| 1 | `note` is present, including JSON null | 400 | Students cannot assign, change, or remove a grade. |
| 2 | `student_id` is present and differs from `acting_student_id` | 400 | You can only enroll yourself. |
| 3 | No registered student for `acting_student_id`, including a programme that lacks a nonempty name | 400 | Only a registered student can enroll in a course. |
| 4 | No existing course for `course_id` | 404 | That course does not exist. |
| 5 | An inscription already exists for that student and course | 409 | You are already enrolled in this course. |

```json
{
  "message": "That course does not exist."
}
```

The business sentences are exact, including the final period.

**Resolved (RF-001).** Constitution 6.0.1 A10 accumulates independent
input-validation failures. It does not accumulate business refusals.
This contract keeps FR-014: one business message, first match.

These conditions do not refuse an enrollment: the student's programme,
an enrollment period, course capacity, a prerequisite, or a course
availability status.

### Data integrity

Not a business refusal and not part of the order above.

| Condition | Status | `message` |
| --- | --- | --- |
| Stored inscription fails domain construction | 500 | Stored inscription data is invalid. |

The transaction rolls back. The body has no `inscription` field.

## Not in this contract

- Login, sessions, or tokens.
- Creating or editing programmes, students, or courses.
- Listing a student's inscriptions.
- Withdrawing, or any other change or delete of an inscription.
- Assigning, changing, removing, or displaying a grade as its own operation.
- An administrator enrolling or approving a student.
- A required course sort order.
- A new failure for a duplicate student email.
