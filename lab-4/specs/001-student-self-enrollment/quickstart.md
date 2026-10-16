# Quickstart: Student Self-Enrollment

Validation guide for browse and self-enrollment. Request and response
details are in
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md).
Stored fields are in [data-model.md](data-model.md).

## Prerequisites

- Python 3.12
- Working directory: `lab-4/`
- Network access only for the first install

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On this machine `python3.12 -m venv` can fail because `ensurepip` is
unavailable. Use the local installer instead:

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

`uv` on this workstation is `/home/devuser/.local/bin/uv` when it is not
on `PATH`. `pyproject.toml` depends on Flask 3.1.3. The `dev` extra
installs pytest and pytest-cov. SQLite comes with Python 3.12. No
linter or type checker is installed.

## Automated validation

```bash
python -m pytest -v --cov=college --cov-branch --cov-report=term-missing
```

The configured `addopts` already include branch coverage of `college`
and fail under 100. This command is a planned Q4 gate. A file total
does not prove a new branch ran, and a green run does not by itself
set the coverage baseline.

A planning review on 2026-10-15 executed this command. It reported 46
passed, 30 branches, and 0 missing, and it warned that module `college`
was previously imported and not measured. That run is not the Q4
baseline. The curl section below was not re-run. `evidence/curl.txt`
is an earlier log.

Expected: every test passes, and the branch report shows no missing
business branch. The suite uses its own database files and does not
read Lab 3.

| Check | Expected |
| --- | --- |
| Registered student enrolls in an existing course | One inscription for that student and course, no note, message "You are enrolled in this course." |
| Student's programme is unrelated to the course | Inscription is still created |
| Same student enrolls in a second course | Second inscription; first inscription unchanged |
| Two students enroll in the same course | Both inscriptions exist |
| No existing courses | `GET /courses` returns `200` and `"courses": []` |
| Several existing courses, including shared names, a course outside the student's programme, and a course already enrolled | `GET /courses` returns each course id, course code, and name |
| Course is missing or incomplete | No write; "That course does not exist." |
| Incomplete course stored beside a valid course | `GET /courses` includes only the valid course. The application course batch also retains an invalid-record diagnostic. The HTTP body has no diagnostic field. |
| Same student and course again, including when that inscription already has a note | No second inscription; existing note unchanged; "You are already enrolled in this course." |
| Person is missing, or lacks a name, an email address, or a programme | No write; "Only a registered student can enroll in a course." |
| Body names a different `student_id` | No write; "You can only enroll yourself." |
| Body includes `note`, including null | No write; "Students cannot assign, change, or remove a grade." |
| One attempt matches more than one business rule | The earliest FR-014 message; no write |
| Two overlapping enrollments for the same student and course | One inscription; the loser receives the already-enrolled outcome |
| `find` returns an invalid inscription | Outcome `integrity`, HTTP 500, message "Stored inscription data is invalid.", transaction rolled back, no write, and no FR-014 sentence. The development seed has no such row, so this check is an automated test rather than a curl against the seed. |
| Missing or non-integer `acting_student_id` or `course_id` | The existing transport sentence; no write |

The current browse tests also expect `course_code` order. That order is
the existing presentation. The specification requires the set.

## Architecture boundaries

From `lab-4/`:

```bash
grep -R -n -E 'flask|sqlite3' src/college/domain src/college/application
grep -R -n -E 'adapters.outbound|sqlite_' src/college/adapters/inbound
grep -R -n -E 'Sqlite[A-Za-z]+\(' src/college --include='*.py'
```

Expected:

- The first command prints nothing. Domain and application do not
  import Flask or `sqlite3`.
- The second command prints nothing. The HTTP adapter does not import
  an outbound adapter.
- The third command finds adapter construction only in `src/college/app.py`.

## Static checks

No lint command and no type-check command are configured. There is
nothing to run for that gate.

## Running HTTP check

Use a fresh database so earlier enrollments do not change the result.

```bash
rm -f /tmp/college-quickstart.sqlite
python -c "from college.app import seed_development; seed_development('/tmp/college-quickstart.sqlite')"
flask --app 'college.app:create_app("/tmp/college-quickstart.sqlite")' run --host 127.0.0.1 --port 5000
```

The seed loads programme `1`, students `1` and `2`, and courses `1`
(`CS101`) and `2` (`CS102`). In another shell:

```bash
curl -sS -D - http://127.0.0.1:5000/courses -o /tmp/courses.json
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 1}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 1}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 2, "course_id": 1}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 99}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 9, "course_id": 1}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 2, "student_id": 2}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 2, "note": null}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1, "course_id": 1, "note": null, "student_id": 2}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"course_id": 1}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": 1}'
curl -sS -D - -X POST http://127.0.0.1:5000/inscriptions \
  -H 'Content-Type: application/json' \
  -d '{"acting_student_id": "1", "course_id": 1}'
sqlite3 /tmp/college-quickstart.sqlite \
  "SELECT student_id, course_id, note FROM inscription ORDER BY student_id, course_id;"
```

Expected, in order:

1. `200` and a `courses` array containing CS101 and CS102, each with
   `id`, `course_code`, and `name`.
2. `201`, "You are enrolled in this course.", inscription `student_id`
   1, `course_id` 1, `note` null.
3. `409`, "You are already enrolled in this course."
4. `201` for student 2 in course 1.
5. `404`, "That course does not exist."
6. `400`, "Only a registered student can enroll in a course."
7. `400`, "You can only enroll yourself."
8. `400`, "Students cannot assign, change, or remove a grade."
9. `400`, the grade sentence again, because a grade attempt also names
   another student and an existing inscription.
10. `400`, "acting_student_id is required."
11. `400`, "course_id is required."
12. `400`, "acting_student_id and course_id must be integers."
13. Stored rows `(1, 1, NULL)` and `(2, 1, NULL)` only.

Stop the Flask process when the curls finish. The test client does not
replace this run.
