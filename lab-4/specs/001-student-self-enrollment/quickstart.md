# Quickstart: Student Self-Enrollment

Validation guide for browse and self-enrollment. Request and response
details are in
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md).
Stored fields are in [data-model.md](data-model.md).

## Prerequisites

- Python 3.12
- Working directory: `lab-4/`
- Network access only to install Flask the first time

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

`pyproject.toml` depends on Flask 3.1.3 and exposes the `college`
package from `src/`. No other runtime dependency is required. SQLite and
`unittest` come with Python 3.12.

## Automated validation

```bash
python -m unittest discover -s tests -v
```

Expected: every test passes. The suite uses an in-memory database and
does not read Lab 3. Fixture students have distinct email addresses.
Fixture courses have distinct course codes. Two courses may share a
name.

| Check | Expected |
| --- | --- |
| Registered student enrolls in an existing course | Inscription for that student and course, no note, message "You are enrolled in this course." |
| Student's programme is unrelated to the course | Inscription is still created |
| Same student enrolls in a second course | Second inscription created; first inscription unchanged |
| No courses stored | `GET /courses` returns `200` and `"courses": []` |
| Several courses, including two with the same name and different codes, one outside the student's programme, and one already enrolled | `GET /courses` returns each course id, course code, and name, ordered by course code |
| Course id does not exist, or the course has no code or no name | No write; message "That course does not exist." |
| Same student and course again, including when that inscription already has a note | No second inscription; existing note unchanged; message "You are already enrolled in this course." |
| Acting id is missing, or the student lacks a name, an email address, or a programme | No write; message "Only a registered student can enroll in a course." |
| Body names a different `student_id` | No write for either student; message "You can only enroll yourself." |
| Body includes `note` | No write; message "Students cannot assign, change, or remove a grade." |
| Two students enroll in the same course | Both inscriptions exist |
| Two concurrent enrollments for the same student and course | One inscription remains; its note is unchanged; the conflicting attempt receives the already-enrolled outcome |

## Manual HTTP check

Start the composition root after the implementation exists:

```bash
flask --app college.app run
```

Load one programme, two students in that programme with different names
and email addresses, and two courses with different course codes. Use
the development seed the implementation provides for this slice, then:

```bash
curl -sS http://127.0.0.1:5000/courses
curl -sS -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 1}'
curl -sS -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 1}'
```

Expected, in order:

1. `200` and a `courses` array. Each item has `id`, `course_code`, and
   `name`.
2. `201`, message "You are enrolled in this course.", and an
   inscription whose `student_id` is 1, `course_id` is 1, and `note` is
   null.
3. `409` and message "You are already enrolled in this course."

A person can complete the browse and the successful enrollment in under
three minutes, with no administrator step.
