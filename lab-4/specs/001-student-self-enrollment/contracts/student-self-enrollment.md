# HTTP Contract: Student Self-Enrollment

Web service contract for browsing courses and self-enrollment.
Business messages follow [spec.md](../spec.md) and
[data-model.md](../data-model.md). Status codes, request shape, and
transport sentences are the existing contract recorded in
[research.md](../research.md).

The service does not define how the caller learned the acting student.
Callers send `acting_student_id` on enrollment.

Base URL is the running Flask service. No path prefix and no version
prefix.

## Browse courses

`GET /courses`

No query parameters. No request body. No student identifier.

### Response

`200` with the set of existing courses. Each course includes its
identifier, course code, and name. A course that lacks a nonempty code
or a nonempty name is absent. The set includes courses outside any
caller's programme and courses a student is already enrolled in. It
does not include a programme, an enrollment flag, or a grade.

The specification requires this set and does not require an order. The
current service returns the set sorted by `course_code` ascending. That
order is the existing presentation.

An invalid stored course is not an element of `courses`. The
application retains an invalid-record diagnostic for that row on the
course batch. This response does not add a field for that diagnostic.

```json
{
  "courses": [
    {
      "id": 1,
      "course_code": "CS101",
      "name": "Introduction to Computer Science"
    },
    {
      "id": 2,
      "course_code": "CS102",
      "name": "Introduction to Computer Science"
    }
  ]
}
```

The example shows two courses that share a name and do not share a
course code, in the order the current service returns. When no existing
course is stored, the status is still `200`:

```json
{
  "courses": []
}
```

## Enroll the acting student

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
| acting_student_id | yes | Integer identifier of the known acting student. |
| course_id | yes | Integer identifier of the course to join. |
| student_id | no | Omitted, or equal to `acting_student_id`, enrolls the acting student. A different value is an attempt to enroll someone else. |
| note | no | A present key, including JSON null, is a grade attempt. Omit the key for a successful enrollment. |

The course code is not an enrollment field. The caller takes `course_id`
from the browse list.

A body that is not a JSON object is read as an empty object.

### Transport outcomes

The adapter decides these before the enrollment use case. They are not
part of the business refusal order. Nothing is written.

| Condition | Status | `message` |
| --- | --- | --- |
| `acting_student_id` is missing | 400 | acting_student_id is required. |
| `course_id` is missing | 400 | course_id is required. |
| Either identifier is present and is not an integer, including a boolean | 400 | acting_student_id and course_id must be integers. |

The specification does not define these three sentences. They are the
sentences this service already returns.

A present `note`, including JSON null, is not a row in this table. The
request has a valid shape. The application decides the grade attempt.
The adapter preserves the key and does not emit the grade sentence.

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

`student_id` is the acting student. `note` is null. No administrator
call is required before this response. The inscription in the body is
the one that was stored. A later attempt for the same student and course
receives the already-enrolled outcome, which is how a caller observes
that the inscription persisted. This contract has no list of
inscriptions.

### Business refusals

The first matching rule wins. The attempt changes nothing.

| Order | Condition | Status | `message` |
| --- | --- | --- | --- |
| 1 | `note` is present, including JSON null. This is application authorization, not a shape failure. | 400 | Students cannot assign, change, or remove a grade. |
| 2 | `student_id` is present and differs from `acting_student_id` | 400 | You can only enroll yourself. |
| 3 | No registered student for `acting_student_id` | 400 | Only a registered student can enroll in a course. |
| 4 | No existing course for `course_id` | 404 | That course does not exist. |
| 5 | An inscription already exists for that student and course | 409 | You are already enrolled in this course. |

A registered student has a nonempty name, a nonempty email address, and
an existing programme. An existing course has a nonempty course code and
a nonempty name.

Refusal body:

```json
{
  "message": "That course does not exist."
}
```

The business sentences are exact, including the final period.

A duplicate refusal does not change the existing inscription or its
note. Any refusal leaves every existing inscription unchanged.

One request that matches more than one business row returns the earlier
row only. A grade attempt that also names another student, an
unregistered student, a missing course, or an existing inscription uses
the grade sentence. An attempt to enroll someone else stops before the
registered-student, course, and duplicate checks.

These conditions do not refuse an enrollment: the student's programme,
an enrollment period, course capacity, a prerequisite, or a course
availability status.

### Data integrity

This is not a business refusal and it is not part of the order above.
The specification is unchanged.

`find` returns `Failure(InvalidInscription)` when the stored row cannot
be constructed as an inscription. The application outcome is
`integrity`. `enroll` does not insert. It asks the unit of work to roll
back, and the transaction does not commit.

| Condition | Status | `message` |
| --- | --- | --- |
| Stored inscription fails domain construction | 500 | Stored inscription data is invalid. |

```json
{
  "message": "Stored inscription data is invalid."
}
```

The body has no `inscription` field. The sentence above is not one of
the business sentences. A grade attempt, an attempt to enroll someone
else, an unregistered student, or a missing course is still decided
first, in that order.

## Not in this contract

- Login, sessions, or tokens.
- Creating or editing programmes, students, or courses.
- Listing a student's inscriptions.
- Withdrawing, or any other change or delete of an inscription.
- Assigning, changing, removing, or displaying a grade as its own operation.
- An administrator enrolling or approving a student.
- A required course sort order.
- A new failure for a duplicate student email.
