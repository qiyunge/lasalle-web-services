# Quickstart: Student Self-Enrollment

Validation guide. Request and response details are in
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md).
Stored fields are in [data-model.md](data-model.md).

This guide does not implement the feature. It checks the running
service and the automated tests.

## Prerequisites

- Python 3.12
- Working directory: `lab-4/`

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

If `python3.12 -m venv` fails because `ensurepip` is unavailable:

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Flask 3.1.3 is the runtime dependency. pytest and pytest-cov are the
dev extra. The approved plan also adds Ruff and Pyright to that extra.
Those two packages are not in `pyproject.toml` until that plan is
approved, so do not install them before then. SQLite comes with Python.

## Automated tests

```bash
python -m pytest -v --cov=college --cov-branch --cov-report=term-missing
```

The configured gate fails when branch coverage of `college` is under
100. For a behavior change, write the failing test first and confirm
it fails for the specified reason before changing the service.

After Ruff and Pyright are installed from the approved plan:

```bash
ruff check src/college
pyright
```

Ruff uses rules `E4`, `E7`, `E9`, and `F`. Pyright uses basic mode.
Both are limited to `src/college`. A genuine error is fixed. It is not
suppressed to force a pass. These commands do not replace the pytest
coverage gate.

Unit tests cover domain construction and the enrollment use case,
including the FR-014 order. Integration tests cover HTTP responses and
the SQLite uniqueness conflict. The Flask test client is not a
substitute for the curl checks below.

## Running service

Start the application from `lab-4/` with its existing entry point and
a database path that is empty or already seeded with a programme
that has a nonempty name, a registered student, and a course. Then:

1. `GET /courses` returns `200` and every existing course, each with
   an identifier, a course code, and a name.
2. `POST /inscriptions` with that student's identifier and an existing
   course returns `201`, the enrolled sentence, and an inscription
   whose note is null.
3. Repeat that post. The response is `409` and "You are already
   enrolled in this course." The stored inscription is unchanged.
4. Post a course identifier that does not exist. The response is
   `404` and "That course does not exist."
5. Post a present `note`, including null, an empty string, or another
   supplied value. The response is `400` and "Students cannot assign,
   change, or remove a grade." Nothing is written. Omitting `note` is
   the successful request in step 2.
6. Post a `student_id`, including one equal to `acting_student_id`.
   The response is `400` and an `errors` array containing
   `target_student_not_accepted` for `student_id`. Nothing is written.
7. Post as an acting student whose programme has no nonempty name.
   The response is `400` and "Only a registered student can enroll in
   a course." Nothing is written.

A request that matches more than one business rule expects only the
FR-014 sentence. RF-001 is resolved: business refusals stay on that
first match.

A request with more than one identifier failure, or with a
target-student field, expects HTTP 400 and an `errors` array of
stable codes and field names, as in
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md).
UD-001 is resolved. One required-identifier failure, with no
target-student field, still expects the single `message` sentence.

`evidence/coverage.txt` and `evidence/curl.txt` record an earlier run
of the current service. They show single-outcome behavior and 100%
branch coverage of the current package. They are not evidence of a
later boundary change. After any code change, record a new pytest
coverage summary and the curl commands with their status codes and
bodies before calling the feature complete.
