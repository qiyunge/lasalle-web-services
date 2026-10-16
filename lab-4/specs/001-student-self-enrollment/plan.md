# Implementation Plan: Student Self-Enrollment

**Branch**: `001-student-self-enrollment` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-student-self-enrollment/spec.md`

## Summary

A registered student browses every existing course and enrolls in one
course without an administrator. The new inscription belongs to the
acting student, names that course, has no grade, and remains observable
after the enrollment succeeds. Duplicate enrollment, a missing course,
an unregistered person, an attempt to enroll someone else, and a grade
attempt fail with the specification sentences and change nothing. When
one attempt matches more than one of those rules, the first match in
the clarified order is the only message.

The current `lab-4` service already implements that behavior with
Python 3.12, Flask 3.1.3, and SQLite. This plan keeps that Full Bridge
shape: domain entities report identity, application use cases own
orchestration and FR-014, the HTTP adapter translates requests and
outcomes, and SQLite adapters implement the outbound ports. Decisions
are in [research.md](research.md). Lab 3 is in the same Git repository
and is not a source for this plan.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Flask 3.1.3. No Flask extensions and no ORM.
pytest and pytest-cov are the configured development dependencies.

**Storage**: SQLite through the standard-library `sqlite3` module. One
connection per request. Enrollment uses one `BEGIN IMMEDIATE`
transaction. `UNIQUE (student_id, course_id)` is the existing atomic
guarantee for overlapping enrollments.

**Testing**: pytest, Flask's test client, SQLite integration tests, and
curl against the running application. Branch coverage uses pytest-cov
on the `college` package.

**Target Platform**: Local Python 3.12 web service.

**Project Type**: web-service

**Performance Goals**: SC-001. A registered student enrolls in an
existing course without an administrator, and the created inscription
is persisted and observable. No throughput target is set.

**Constraints**: Constitution 2.0.4. Domain stays free of third-party
code. Application owns business refusal order. Transport shape stays at
the HTTP boundary. Rejected operations do not write. Exact specification
messages stay. No new business rule is added for an unresolved case.

**Scale/Scope**: One college service. This slice browses courses and
creates a self-enrollment. Programmes, students, and courses already
exist. Grade management, withdrawal, and catalogue administration stay
out of scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution 2.0.4. Checked against the accepted specification and the
current `lab-4` code before research.

| Gate | Result |
| --- | --- |
| B1. A student belongs to an existing programme. | Pass. A missing programme is not a registered student and uses that specification sentence. Programme match does not filter browse or enrollment. |
| B2. Student identifier, nonempty name, nonempty unique email. | Target: `Student.create` returns a failure Result when name or email is not nonempty. `enroll` maps that failure, and a missing row, to the specification sentence. This slice does not write students, so it adds no duplicate-email failure. Current code still uses a reporting predicate. |
| B3. Course identifier, nonempty unique code, nonempty name. Names may repeat. | Target: `Course.create` returns a failure Result when code or name is not nonempty. Enrollment uses the existing course sentence. Browse keeps the valid courses and the invalid-record diagnostics. Current code still filters with `is_complete`. |
| B4. An inscription references an existing student and course, once per pair. | Pass. The use case loads both, checks the pair, and interprets a persistence conflict as already enrolled. |
| B5. A note is optional. An assigned note uses the feature's range. | Pass. This slice writes no note and states no range. |
| B6. Missing and conflicting records fail explicitly. | Pass. Each specified failure has its sentence. A refusal does not write. |
| B7. A student may browse and self-enroll, and cannot enroll someone else or change a grade. | Pass. No administrator step and no withdrawal operation. |
| A1. Distinct application and domain, infrastructure outside the core. | Pass. The current package already splits them. |
| A2. Domain owns and enforces its invariants, with no third-party imports. | **Pass for the target design.** Public construction is a domain factory that returns `Result`. An invalid entity is not returned. Current constructors do not do this yet. The work is in the gap matrix, not a waiver. |
| A3. Application owns driving use cases and outbound coordination. | Pass. `browse` and `enroll` coordinate the ports. They do not import adapters, Flask, or `sqlite3`. |
| A4. Inbound adapter translates the request and the outcome. | Target: the adapter owns request shape and maps `result.outcome`. A grade attempt stays an application decision. Inspection: shape checks and the grade check both still run inside `enroll`. |
| A5. Outbound ports are application-owned. Adapters translate rows. | Pass. `PersistenceConflict` crosses the boundary. `IntegrityError` and `sqlite3.Row` do not. |
| A6. Core owns the boundary contract. No internal DTO is required. | Pass. Domain types are shared inside the core. JSON and rows are translated at the adapters. |
| A7. The use case preserves invariants across the write. | Pass. One unit of work wraps the enrollment reads and the insert. The adapter rolls back and reports the conflict. The use case chooses the message. |
| A8. Programme, student, course, and inscription stay distinguishable. | Pass. Each capability has its own module and repository. Enrollment calls one port per capability. Browse calls the course port. |
| E1. Python 3.12, Flask, and SQLite. | Pass. |
| E2. Follow established conventions. | Pass. The plan reuses the current modules, messages, status map, and ports. |
| E3. A new dependency needs a demonstrated need. | Pass. No new runtime or development dependency. |
| E4. Expected failures stay explicit. | Pass. Outcomes are named. The HTTP status is a translation of the outcome. |
| E5. Red, Green, Refactor for new or changed observable behavior. | **Planned.** This review did not run a Red cycle. The pytest run recorded below is the current suite, not Red or Green for a behavior change. |
| E6. Feature-local choices stay in the feature. | Pass. Status codes, transport sentences, and the current course sort stay in this feature's contract. |
| Q1. Specification audience, behavior, failures, exclusions, and scenarios. | Pass. The accepted spec contains them. |
| Q2. pytest at unit, integration, and HTTP where those levels can observe the behavior. | **Partial.** Executed this review: 46 existing tests passed. Inspection: those tests omit most FR-014 combinations. The missing cases are a gap. |
| Q3. Run the configured lint and type checks. | Inspection of `pyproject.toml`: no linter and no type checker are configured. There is no lint result to pass. This plan does not add a tool. |
| Q4. 100% branch coverage of new or modified business code, from branch-level data. Overall coverage stays at a baseline taken from a verified report and changed only by an explicit decision. | **Not passed.** The planned scope is `college` with `--cov-branch`. This review ran that command and does not adopt the run as the baseline. See Verification obligations. |
| Q5. curl against the running application for user-facing HTTP behavior. | **Planned. Not passed.** Commands are in [quickstart.md](quickstart.md). This review did not run them. |
| Q6. Completion report after tests, coverage, static checks, and HTTP verification. | **Planned.** This planning review does not declare the feature complete. |

**Gate result:** The target design resolves A2. It does not waive the
current constructors. Q4 and Q5 are planned gates without a pass. The
business sentences and FR-014 order stay as specified. Sequencing
belongs to `/speckit-tasks`.

### Post-design re-check

Re-checked after [research.md](research.md), [data-model.md](data-model.md),
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md),
and [quickstart.md](quickstart.md).

The data model keeps the B1–B7 fields and the FR-014 order, and it does
not define tables or indexes. The contract separates request-shape
failures, business authorization, and the integrity failure.
`Failure(InvalidInscription)` is outcome `integrity`, HTTP 500, and a
rollback. It is not an FR-014 rule. Direct dataclass construction
raises `ConstructionError` and does not return an invalid entity.
`Programme` has no factory. Course order stays presentation. The
quickstart curl gate was not executed in this review.

Post-design, the A2 target includes the factories, the constructors,
and the course batch. Q4 is still not passed. Q5 and Q6 are still
planned. Those quality gates are not waivers, and A2 is not an
approved exception.

## Project Structure

### Documentation (this feature)

```text
specs/001-student-self-enrollment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── student-self-enrollment.md
└── tasks.md              # /speckit-tasks, not updated here
```

### Source Code (repository root)

Paths are relative to `lab-4/`. This is the current tree plus
`domain/result.py`, the one module this decision adds.

```text
pyproject.toml
src/college/
├── domain/
│   ├── result.py
│   ├── programme.py
│   ├── student.py
│   ├── course.py
│   └── inscription.py
├── application/
│   ├── ports.py
│   ├── browse_courses.py
│   └── enroll_student.py
├── adapters/
│   ├── inbound/
│   │   └── http.py
│   └── outbound/
│       ├── sqlite_programme_repository.py
│       ├── sqlite_student_repository.py
│       ├── sqlite_course_repository.py
│       ├── sqlite_inscription_repository.py
│       └── sqlite_unit_of_work.py
└── app.py
tests/
├── unit/
│   ├── test_browse_courses.py
│   └── test_enroll_student.py
└── integration/
    ├── test_http_courses.py
    ├── test_http_enrollment.py
    ├── test_inscription_concurrency.py
    └── test_development_seed.py
```

**Structure Decision**: One web service under `src/college`. Capability
modules do not import one another. They may import `domain.result`,
which holds no business fields. Domain modules import neither Flask nor
`sqlite3`. `browse` and `enroll` depend on ports. `http.py` translates
JSON and maps the use-case outcome. Outbound modules own SQL.
`app.py` constructs the adapters and opens one connection for each
request. `seed_development` is support for the manual HTTP check.

Compliance is judged from dependency direction and responsibility, not
from file placement.

## Architecture

The core is the domain plus the application. Delivery and storage stay
outside it.

**Domain.** `Programme`, `Student`, `Course`, and `Inscription` are the
entities. Each public construction path is a factory that returns
`Result`. `Success` holds the entity. `Failure` holds an invalid-record
value and no user-facing sentence. Domain code uses the standard
library only.

**Application.** `browse` returns the course batch: valid courses and
the invalid-record diagnostics. `enroll` applies FR-014, calls the
outbound ports, and returns `EnrollmentResult`. That result carries
`outcome`, the specification message, and, on success, the created
`Inscription`. A missing row and an invalid restored record stay
distinct on the port result. `enroll` decides that both mean the
existing not-registered sentence or the existing missing-course
sentence. `PersistenceConflict` remains the write-conflict signal. It
is not the validation or data-recovery path.

**Driving contracts.** `browse(courses)` and `enroll(...)` are the
use-case contracts the inbound adapter calls. They are not given a
second Protocol. Nothing else implements them.

**Inbound.** The HTTP adapter reads the JSON body. Its decision is
request shape: a JSON object, an integer `acting_student_id`, and an
integer `course_id`. A boolean is not an integer. It then calls one
use case and translates `result.outcome` with the existing status map.
It does not decide a grade attempt, whether the caller is enrolling
someone else, whether a student is registered, whether a course exists,
or whether a duplicate inscription exists. A present `note`, including
JSON null, is passed through. The application decides that this is a
grade attempt.

**Outbound.** Each repository reads or writes only its own capability
and returns domain entities. The unit of work begins and ends the
transaction. The inscription repository turns `IntegrityError` into
`PersistenceConflict`.

**Translation.** JSON becomes use-case arguments in `http.py`. Rows
become entities in the repositories. The core does not receive a Flask
request or a SQLite row. No extra DTO is inserted between the
application and the domain.

**Wiring.** Production adapters are constructed in `app.py`. Tests bind
fakes at the same use-case arguments. A use case does not construct an
adapter.

**Capability references.** A student stores a programme identifier. An
inscription stores a student identifier and a course identifier. Those
are values on the owning entity. A repository does not read another
capability's table. One use case does not call the other.

## Business behavior

The implementation matches the accepted specification and adds no rule
the specification left open.

- Browse shows every existing course, including courses outside the
  student's programme and courses already enrolled. Shared names are
  both shown. Incomplete courses are omitted.
- Self-enrollment needs no administrator. The inscription names the
  acting student and the chosen course and has no grade.
- A second course creates a separate inscription. Two students may
  enroll in the same course.
- Business refusal order is unchanged: grade attempt; enrolling
  someone else; unregistered student; missing course; duplicate
  enrollment.
- Every refusal leaves stored inscriptions unchanged. A duplicate
  leaves an existing note unchanged.
- Programme, enrollment period, capacity, prerequisite, and
  availability do not refuse enrollment.

### Request shape and business authorization

These are different decisions. They can both produce HTTP 400. The
status is a mapping of an outcome. It does not make a grade attempt a
shape error.

| Decision | Owner | What counts | Result |
| --- | --- | --- | --- |
| Request shape | HTTP adapter, before `enroll` | Body is not a JSON object. `acting_student_id` or `course_id` is missing or is not an integer. A boolean is not an integer. | The three sentences the service already returns. No use-case call. Not part of FR-014. |
| Grade attempt | Application, FR-014 rule 1 | A present `note` key, including JSON null. The body is otherwise well formed. | Outcome `forbidden` and "Students cannot assign, change, or remove a grade." The adapter maps `forbidden` to 400. |
| Enroll someone else | Application, FR-014 rule 2 | `student_id` is present and differs from `acting_student_id`. | "You can only enroll yourself." |
| Later business rules | Application, FR-014 rules 3–5 | Registered student, existing course, then duplicate inscription. | The specification sentence for that rule. |

The adapter translates `note` with `payload.get("note", ABSENT)`. It
must not drop a present key and must not treat JSON null as an omitted
field. It must not emit the grade sentence. `enroll` sees a supplied
note and applies rule 1 before the other business rules.

Inspection of the current code: the shape checks and the grade check
both run at the start of `enroll`. The grade check is already in the
application, and it already runs before the other-student check. The
planned move is only the three shape sentences, from `enroll` to the
HTTP adapter. The grade check stays in `enroll`. HTTP tests that assert
the shape sentences stay. They are not deleted to make a suite pass.

## Persistence and consistency

| Port | Operations this slice uses | Result the adapter returns |
| --- | --- | --- |
| Programme | `get` | `Success(Programme)` or `Failure(Missing)` |
| Student | `get` | `Success(Student)`, `Failure(Missing)`, or `Failure(InvalidStudent)` |
| Course | `get` | `Success(Course)`, `Failure(Missing)`, or `Failure(InvalidCourse)` |
| Course | `list_all` | `CourseList` of valid `Course` values and `InvalidCourse` diagnostics |
| Inscription | `find`, `add` | `find` returns `Success(Inscription)`, `Failure(Missing)`, or `Failure(InvalidInscription)`. `add` still returns the created inscription or raises `PersistenceConflict`. |
| Unit of work | begin, commit on success, roll back on exception, and `rollback` when the application asks | A business `Result` does not raise, so that path commits with no insert. `enroll` calls `rollback` for `InvalidInscription` before it returns `integrity`. |

Enrollment holds one connection for all five collaborators. The use
case starts the unit of work before the business reads and the insert.
`BEGIN IMMEDIATE` makes an overlapping enrollment wait. On a clean
exit the unit of work commits. On any exception, or after `rollback`,
it rolls back and does not commit. `PersistenceConflict` is caught
outside the unit of work, after that rollback, and becomes the
already-enrolled outcome. `InvalidInscription` does not raise.
`enroll` calls `rollback` and then returns `integrity`.

`add` inserts `note` as null. The unique `(student_id, course_id)` pair
is the atomic guarantee. The repository does not choose the user-facing
sentence. A restored row is passed through the domain factory. The
adapter returns that `Result` or places the failure on `CourseList`.
It does not drop an invalid course row and it does not turn the failure
into a specification sentence. Browse opens its own connection, lists
courses, and does not join the enrollment transaction. A `Failure`
returned for a missing or invalid student or course is an expected
result inside the unit of work. The use case returns the business
outcome. The unit of work then commits because no exception was raised.
Nothing was inserted.

No new repository, transaction type, or index is added. Email and
course-code uniqueness have no write path in this slice, so this plan
does not add a storage constraint for them.

## Verification obligations

A planned gate is an obligation. It is not a pass. A pass requires
executed evidence of the kind that gate names. Implementation order
belongs to `/speckit-tasks`.

**Executed this review, 2026-10-15.** From `lab-4/`,
`.venv/bin/python -m pytest` with the configured `--cov=college
--cov-branch` reported 46 passed, 224 statements, 30 branches, 0
missing, and a tool total of 100%. Coverage warned that module
`college` was previously imported and not measured. `student.py` and
`course.py` are listed with 0 branches, so that report does not show
branch coverage of `has_identity` or `is_complete`. This run is
evidence that the current tests passed. It is not a Q4 pass, and it is
not adopted as the coverage baseline.

**Stored logs, read and not re-run.** `evidence/coverage.txt` records
an earlier 46-passed, 30-branch run. `evidence/curl.txt` records an
earlier curl session. This review did not execute curl.

**Q4, not passed.** The planned measure is branch coverage of `college`
with the configured pytest-cov scope. New or modified business branches
need the branch table, not a file percentage alone. Overall coverage
must not fall below a baseline taken from a verified report of that
same scope. The baseline changes only by an explicit decision. Neither
the stored log nor this review's run is that decision.

**Q5, planned and not passed.** Curl against the running Flask process
is specified in [quickstart.md](quickstart.md). The Flask test client
does not replace it.

**Q3, no command.** No linter or type checker is configured. Recording
that fact is the inspection result. It is not a lint pass.

**E5, planned.** For observable behavior that is new or changed, the
failing run is Red and the later passing run is Green. Both are
observed during implementation and named in the completion report.
This plan does not require a permanent evidence file. A test that
passes the first time is not a Red cycle. Existing tests stay. They
are not weakened, deleted, or excluded to reach a green run or a
coverage number.

**Changed behavior still planned.** Moving the three shape checks to
the adapter preserves the HTTP sentences. Existing HTTP tests must
pass before and after that move. Domain factories and constructor rejection are new observable
behavior. The Red tests show that `create` returns `Failure` and that
the matching dataclass call raises `ConstructionError`, before either
path enforces the invariant. The enrollment messages for an incomplete
student or course stay. Tests that now build an illegal entity change
their setup to a port `Failure`. They keep the same message assertion.
A separate test expects outcome `integrity`, a rollback, and HTTP 500
when `find` returns `Failure(InvalidInscription)`.

**Acceptance set.** Automated tests derived from the specification
cover browse, successful self-enrollment, the persisted grade-free
inscription, a second course, two students in one course, each single
refusal, and simultaneous business violations. The simultaneous cases
include a grade attempt combined with each later rule, an attempt to
enroll someone else combined with each later rule, an unregistered
student combined with a missing course, and a missing course combined
with an existing inscription. The earliest FR-014 message wins, and
the stored inscriptions stay unchanged. Overlapping enrollments keep
one inscription.

**Levels.** Domain tests observe identity and completeness. Application
tests call the use cases through fake ports, including a fake that
raises `PersistenceConflict`. SQLite tests observe the conflict, the
rollback, and the surviving row. HTTP tests observe status and body.
A level is required where it can see the behavior.

**Coverage.** Planned gate, not a pass: new or modified business
branches are covered at 100% on the branch report for `college`, using
pytest with `--cov=college --cov-branch`. Overall branch coverage uses
that same scope. Third-party code, generated code, and tests are
excluded. No further exclusion is added. A file total does not close
this gate, and this review does not set the baseline.

**Architecture.** Source reading: domain and application do not import
Flask or `sqlite3`, the HTTP adapter does not import an outbound
adapter, and SQLite adapters are constructed in `app.py`. The
quickstart grep was not executed in this review.

**Static checks.** No linter and no type checker are configured. The
completion report states that. Choosing a tool would be a separate
dependency decision.

**Running HTTP.** The planned curl set covers browse, the created
inscription, the duplicate that shows it persisted, the other
seed-reachable refusals, and a combined grade attempt. That set was
not executed in this review.

## Brownfield gap matrix

"Inspection" means the current source or test text was read. "Executed"
means the test was in the pytest run on 2026-10-15 (46 passed). That
run is not a Q4 pass. Curl was not re-run; `evidence/curl.txt` was only
read.

| Requirement | Implementation, by inspection | Test evidence | Change this decision requires |
| --- | --- | --- | --- |
| FR-001–FR-003 browse set and fields | `browse` keeps courses where `is_complete` is true and sorts by `course_code`. HTTP returns `id`, `course_code`, and `name`. | Executed: browse unit tests and HTTP course tests. They also lock code order. | `CoursePort.list_all` returns `CourseList`. The repository records every invalid row on `invalid`. `browse` shows `courses` and keeps `invalid`. HTTP still returns only the valid courses. Spec order stays out of scope. Existing order assertions stay. |
| FR-004–FR-006 self-enrollment, no grade, success sentence | `enroll` inserts the acting student and course with no note and returns the success sentence. No administrator step. | Executed: unit success tests and HTTP 201, which returns the inscription. | Fakes return `Success` for the loaded student, programme, and course. The success message and the inscription fields stay. |
| FR-007 missing or incomplete course | Missing row or `is_complete` false becomes "That course does not exist." No insert. | Executed: unit cases for empty and `None` code or name; HTTP missing id. | Domain: `Course.create` failure tests, Red first. Port: `get` returns `Failure(Missing)` or `Failure(InvalidCourse)`. Adapter test: a blank stored code is `InvalidCourse`, not a `Course`. Application test: both failures use "That course does not exist." and write nothing. The message assertion stays. |
| FR-008 duplicate, including overlap, existing note kept | `find` before insert. `IntegrityError` becomes `PersistenceConflict`. `enroll` maps that to the already-enrolled sentence after rollback. | Executed: unit duplicate, unit conflict fake, HTTP duplicate with note `A`, concurrency test. | `find` returns `Success(Inscription)` for a valid row, including note `A`. `Missing` means not enrolled. `PersistenceConflict` stays the write conflict. `InvalidInscription` is the integrity outcome, not this sentence. |
| FR-009 registered student | Missing student, failed `has_identity`, or missing programme uses the not-registered sentence. | Executed: unit cases for a missing student, blank or `None` name or email, and a missing programme. HTTP covers an unknown id and a deleted programme. | Domain: `Student.create` failure tests, Red first. Port: `Failure(Missing)` or `Failure(InvalidStudent)`. Programme absence stays `Failure(Missing)`. Application maps all three to the not-registered sentence. Adapter test for a blank stored name. HTTP test for that row is still absent and is required. Email uniqueness still has no write path. |
| FR-010 enroll someone else | A different `student_id` returns the yourself sentence and does not write. The same id still enrolls. | Executed: unit and HTTP. | No message change. The check stays before the port load. |
| FR-011 grade attempt | A supplied `note`, including `None`, returns the grade sentence before the other business rules. | Executed: unit `None` and `"A"`; HTTP `note: null`. | No message change. The check stays in `enroll` before a load, so a grade attempt does not depend on a Result from the repository. |
| FR-012 no extra refusals | No period, capacity, prerequisite, availability, or programme-match refusal. | Executed: an unrelated programme still enrolls. | No new refusal. The unrelated-programme test stays. |
| FR-013 failed attempt writes nothing | Business returns happen before `add`. The conflict path rolls back. | Executed: failure tests assert an empty or unchanged inscription list. | A validation `Failure` is returned, not raised, so the unit of work does not roll back an empty transaction into a different outcome. Tests still assert no inscription change. |
| FR-014 precedence | After the shape checks, `enroll` uses the specified five-rule order. | Executed: one combination, grade over enrolling someone else (`note="A"`, `student_id=2`). | The five sentences and their order stay. Add the missing combination tests, including a grade attempt that would also be an invalid student or a missing course. The grade sentence still wins. |
| SC-001 persisted, observable inscription | The 201 body contains the inscription. A second attempt for that pair is already enrolled. | Executed: HTTP 201 body; duplicate and concurrency tests read the stored row. `evidence/curl.txt` shows 201, then 409, then rows `(1, 1)` and `(2, 1)`. That file was not re-run. | No contract change. Q5 is not passed. |
| SC-002–SC-005 | Same paths as the FR rows above. | Executed where the FR row says executed. | Same test updates as FR-007, FR-009, and FR-014. HTTP still omits an incomplete course. |
| Request shape | The three shape sentences are returned by `enroll`, not by the adapter. | Executed: unit and HTTP tests for a missing id, a non-integer id, and a non-object body. | Move the three sentences to the adapter. They stay out of FR-014 and out of `Result`. |
| Domain construction | `Student(...)` and `Course(...)` accept empty text. Predicates report it. Repositories build those objects from rows. | Executed tests build the illegal values and expect the specification sentences. | `Student`, `Course`, and `Inscription` gain `create` plus `__post_init__`. `Programme(...)` rejects a non-integer id and has no factory. Tests cover both the `Failure` path and the `ConstructionError` path. Message assertions for student and course stay. |

## Specification gaps

These items stay unresolved on purpose. The plan does not invent a
business rule for them, and it does not amend the specification.

| Gap | What this plan does |
| --- | --- |
| The specification does not define transport failure sentences. | Reuse the three sentences the service already returns. Keep them out of FR-014. |
| The specification does not define how a grade attempt or an attempt to enroll someone else is encoded. | Reuse a present `note` key, including JSON null, and a different `student_id`. |
| Display order is out of scope. | Keep the current `course_code` sort as presentation. The business outcome is the set. Existing order assertions stay. |
| Duplicate student email has no specified failure or comparison beyond the stored value. | Add no failure and no write path. |
| A grade range is not stated. | Write no grade and state no range. A restored note string remains a valid inscription. |
| Recognition of the acting student is out of scope. | Keep `acting_student_id` on the enrollment request. Add no login design. |
| The specification has no business sentence for a structurally invalid inscription. | The specification stays unchanged. The contract maps outcome `integrity` to 500 and "Stored inscription data is invalid." That sentence is not added to FR-014. |

## Domain construction

This is the accepted resolution of A2. The current constructors are
not yet this design. Expected validation and data-recovery failures
are `Result` values. They are not exceptions used as control flow.

**Result.** `domain/result.py` defines `Success` and `Failure` with the
standard library. `Success` carries the entity. `Failure` carries one
error value. The type has no business fields. Capability modules may
import it. They still do not import each other.

**Factories and constructors.** `Student.create`, `Course.create`, and
`Inscription.create` are the recovery paths. Each returns `Result`.
An invariant failure returns `Failure` and does not raise. `Programme`
has no factory and no invalid-record value. Its only field is the
identifier.

The dataclass constructor is also a public path. `__post_init__` runs
the same invariant and raises `ConstructionError` when the value is
invalid, so the call does not return an entity. `ConstructionError`
lives in `domain/result.py`. The factory does not use it. The factory
checks first and calls the constructor only after the value is valid.

| Path | Valid | Invalid |
| --- | --- | --- |
| `Student.create` and `Student(...)` | `id` and `programme_id` are integers. Name and email are nonempty strings. | `Failure(InvalidStudent)` from `create`. `ConstructionError` from `Student(...)`. |
| `Course.create` and `Course(...)` | `id` is an integer. Course code and name are nonempty strings. | `Failure(InvalidCourse)` from `create`. `ConstructionError` from `Course(...)`. |
| `Programme(...)` | `id` is an integer. | `ConstructionError`. No `Result` and no business sentence. |
| `Inscription.create` and `Inscription(...)` | `id`, `student_id`, and `course_id` are integers. `note` is `None` or a string. | `Failure(InvalidInscription)` from `create`. `ConstructionError` from `Inscription(...)`. |

`InvalidStudent` and `InvalidCourse` carry the identifier and no
sentence. `InvalidInscription` carries no sentence. A stored grade
string is valid. This feature states no grade range. The inscription
factory does not check that the student or the course exists.

**Verification.** Tests show both public paths before the constructors
enforce them. `Student(1, "", "ada@college.test", 1)` and the matching
`Course(...)` and `Inscription(...)` calls raise `ConstructionError`
and do not produce an entity. The same arguments passed to `create`
return `Failure` and do not raise. A valid `create` returns `Success`
whose value is the entity. `Programme(1)` returns a programme.
`Programme(None)` raises `ConstructionError`. No test introduces an
`InvalidProgramme` outcome.

**Ports.** `Missing` lives on the outbound port. It means no row. It is
not an invalid record.

`StudentPort.get` and `CoursePort.get` return `Result` of the entity,
`Missing`, or the domain invalid value. `ProgrammePort.get` returns
`Success(Programme)` or `Failure(Missing)`. The repository builds a
programme with `Programme(id)` because a stored identifier is valid.
`InscriptionPort.find` returns `Success(Inscription)`,
`Failure(Missing)`, or `Failure(InvalidInscription)`. `Missing` on
`find` means the student is not enrolled.

`CoursePort.list_all` returns `CourseList`. That value holds the valid
`Course` entities and the `InvalidCourse` diagnostics from the same
read. The repository appends each factory failure to `invalid`. It does
not drop the row. `CourseList` is the port result. It does not copy
course fields into another object.

**Application.** `enroll` keeps FR-014. After the grade attempt and the
other-student check:

- `Failure(Missing)` or `Failure(InvalidStudent)` for the acting
  student, or `Failure(Missing)` for that student's programme, is
  "Only a registered student can enroll in a course."
- `Failure(Missing)` or `Failure(InvalidCourse)` is "That course does
  not exist."
- `Success(Inscription)` is "You are already enrolled in this course."
- `Failure(Missing)` from `find` continues to `add`.

`Failure(InvalidInscription)` is an internal data-integrity failure.
It is not a business refusal and it is not a sixth FR-014 rule. The
five business rules stay in the specification order. This failure is
reached only when those rules that are checked before `find` have
passed. `enroll` does not call `add`. It calls `rollback` on the unit
of work, then returns `EnrollmentResult` with outcome `integrity`,
message "Stored inscription data is invalid.", and no inscription.
The unit of work rolls back on `rollback` even though no exception was
raised, and it does not commit. Existing rows stay unchanged. The HTTP
adapter maps `integrity` to 500 and that message. It does not choose
the integrity outcome. A business `Failure` for a student or a course
still returns without `rollback`; that transaction commits with no
insert.

`browse` returns the `CourseList`. The shown courses are `courses`.
`invalid` stays on the result the application returns. The HTTP adapter
maps `courses` only. The specification does not add a diagnostic field
to the course list.

Programme existence stays an application check. Email uniqueness and
course-code uniqueness stay collection rules. This feature does not
write those collections, so the factories do not invent a duplicate
failure.

**Adapters.** Each SQLite `get` or `find` returns `Failure(Missing)`
when the row is absent. A programme row is `Programme(id)`. A student,
course, or inscription row is the factory `Result`, returned unchanged.
`list_all` builds a `CourseList` from every row. No adapter chooses a
specification sentence or the integrity sentence.

## Constitution conflicts

**Q3, E3, and the request for lint and type checking.** No tool is
configured. Q3 forbids adding one as a side effect, and E3 requires a
demonstrated need before a new dependency. This plan selects neither
Ruff nor mypy.

**E5 and a required Red run.** E5 requires Red and Green when observable
behavior is new or changed. It requires the existing tests before and
after when behavior is preserved. A passing current suite is not Red
evidence for a later change.

## Complexity Tracking

No violation is approved as an exception. The A2 target is the domain
`Result` factories and `CourseList` above. Q4 and Q5 remain unpassed
quality gates.
