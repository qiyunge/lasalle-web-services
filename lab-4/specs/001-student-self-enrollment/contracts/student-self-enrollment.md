# HTTP Contract: Student Self-Enrollment

Web service contract for browsing courses and self-enrollment.
Messages and fields follow [spec.md](../spec.md) and
[data-model.md](../data-model.md). Status codes and request shape are
recorded in [research.md](../research.md).

The service does not define how the caller learned the acting student.
Callers send `acting_student_id` on enrollment.

Base URL is the running Flask service. No path prefix and no version
prefix.

## Browse courses

`GET /courses`

No query parameters. No request body.

### Response

`200` with every valid course, ordered by `course_code` ascending.
Each course includes its identifier, course code, and name.

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
course code. When no valid course exists, the status is still `200`:

```json
{
  "courses": []
}
```

The list includes courses outside any caller's programme and courses a
student is already enrolled in. It does not include a programme, an
enrollment flag, or a grade.

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
| student_id | no | If present and equal to `acting_student_id`, the enrollment is still for the acting student. If present and different, the request is refused. |
| note | no | If the key is present, the request is a grade attempt and is refused. Omit the key for a successful enrollment. |

The course code is not an enrollment field. The caller takes `course_id`
from the browse list.

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
call is required before this response.

### Refusals

The first matching rule wins. Nothing is written.

| Condition | Status | `message` |
| --- | --- | --- |
| `acting_student_id` is missing | 400 | acting_student_id is required. |
| `course_id` is missing | 400 | course_id is required. |
| Either id is present and is not an integer | 400 | acting_student_id and course_id must be integers. |
| `note` is present | 400 | Students cannot assign, change, or remove a grade. |
| `student_id` is present and differs from `acting_student_id` | 400 | You can only enroll yourself. |
| No student with `acting_student_id`, or that student lacks a name, an email address, or an existing programme | 400 | Only a registered student can enroll in a course. |
| No course with `course_id`, or that course lacks a course code or a name | 404 | That course does not exist. |
| An inscription already exists for that student and course | 409 | You are already enrolled in this course. |

Refusal body:

```json
{
  "message": "That course does not exist."
}
```

The business sentences in the table are exact, including final periods.
The three request-shape messages are contract errors.

A duplicate refusal does not change the existing inscription or its
note. Any refusal leaves every existing inscription unchanged.

These conditions do not refuse an enrollment: the student's programme,
an enrollment period, course capacity, a prerequisite, or a course
availability status.

## Not in this contract

- Login, sessions, or tokens.
- Creating or editing programmes, students, or courses.
- Listing a student's inscriptions.
- Withdrawing, or any other change or delete of an inscription.
- Assigning, changing, removing, or reading a grade as its own operation.
- An administrator enrolling or approving a student.
