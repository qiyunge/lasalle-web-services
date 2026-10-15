# Implementation Plan: Student Self-Enrollment

**Branch**: `001-student-self-enrollment` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-student-self-enrollment/spec.md`

## Summary

A registered student browses every existing course and enrolls in one
course without an administrator. The new inscription belongs to the
acting student, names that course, and has no grade. Duplicate
enrollment, an unknown course, an unregistered person, an attempt to
enroll someone else, and an attempt to send a grade fail with the
sentences in the spec and change nothing.

Lab 4 is a greenfield Python 3.12 service governed by constitution
1.3.0. A stored student has an identifier, a name, a unique email
address, and an existing programme. A stored course has an identifier,
a unique course code, and a name. Flask 3.1.3 accepts HTTP. Use cases
talk to repository ports. SQLite is reached only through the
standard-library `sqlite3` module. This slice does not create students
or courses, and it does not turn those identity rules into a SQL
schema. Lab 3 is in the same Git repository and is not a source for
this plan. Decisions are recorded in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Flask 3.1.3. No Flask extensions and no ORM.

**Storage**: SQLite via the standard-library `sqlite3` module. Domain
invariants are not defined as tables or indexes.

**Testing**: pytest, Flask's test client, and in-memory SQLite.

**Target Platform**: Local Python 3.12 web service.

**Project Type**: web-service

**Performance Goals**: A student can browse the course list and enroll
in an existing course in under 3 minutes, without an administrator
(SC-001). No separate throughput target is set.

**Constraints**: Hexagonal boundaries; thin Flask routes; business rules
outside Flask and SQLite adapters; repository ports; one transaction
around inscription creation; separate student, course, programme, and
inscription modules; student and course identity invariants; exact spec
messages; no authentication design; no Lab 3 material.

**Scale/Scope**: One college service. This slice only browses courses
and creates a self-enrollment. Programmes, students, and courses already
exist and already satisfy the identity invariants. Grade management,
withdrawal, and catalogue administration are out of scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution v1.3.0. Checked before research against the spec and the
technical context above.

| Gate | Result |
| --- | --- |
| I. A student belongs to an existing programme. | Pass. Enrollment treats a missing programme as not registered and uses the spec sentence. Browse and enrollment do not filter by programme match. |
| II. An inscription references an existing student and an existing course. | Pass. Both are loaded before insert. A missing course uses "That course does not exist." |
| III. A student has at most one inscription for the same course. | Pass. The use case owns the rule and interprets a persistence conflict as already enrolled. The database only supplies the atomic guarantee. |
| IV. An inscription may have no grade. | Pass. This slice writes no note and states no permitted grade range. |
| V. Missing or conflicting records fail explicitly. | Pass. Each spec failure has its sentence. A refusal does not write. |
| VI. A student may browse and self-enroll, with no grade required, while enrollment rules stay in force. | Pass. No administrator step. Programme, capacity, prerequisites, periods, and availability do not refuse enrollment. |
| VII. A student cannot enroll someone else, cannot change a grade, and is not granted withdrawal. | Pass. Those attempts write nothing. No withdrawal operation is included. |
| VIII. Python 3.12, Flask, and SQLite. | Pass. |
| IX. Domain independent of frameworks; use cases through ports; inbound and outbound adapters. | Pass. See the source layout below. |
| X. Thin routes; no business rules in Flask or SQLite; repository ports; transactions preserve invariants. | Pass. The HTTP adapter parses the request, calls one use case, and maps that use case's outcome to HTTP. It does not decide eligibility or existence. Insert runs in one transaction. |
| XI. Student, course, programme, and inscription stay bounded. | Pass. Cross-capability references are identifier values only. Repositories do not cross capabilities. Use cases do not call one another. |
| XII. Existing conventions and minimal dependencies. | Pass. Lab 4 has no application code yet. Runtime additions are Flask, as required, plus standard-library `sqlite3`. pytest is the demonstrated test dependency required by Principle XVII. |
| XIII. Unsettled design questions go to the architect. | Pass. Choices required to write the contract are recorded in research.md. The spec's sentences and out-of-scope list are unchanged. |
| XIV. A student has an identifier, a required name, a required unique email address, and an existing programme. | Pass. The data model records those fields. This slice does not create students and does not prescribe a schema or index for email uniqueness. An incomplete student is not registered. |
| XV. A course has an identifier, a required unique course code, and a required name. Names need not be unique. | Pass. Browse returns all three. This slice does not create courses and does not prescribe a schema or index for course-code uniqueness. |
| Feature-spec compliance: audience, behaviour, failure messages, out of scope. | Pass. The source spec already states all four. |

No gate failed. Complexity Tracking is empty.

### Post-design re-check

Re-checked after [data-model.md](data-model.md),
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md),
and [quickstart.md](quickstart.md).

The data model includes student name and email, course code and name,
optional inscription note, and one inscription per student and course.
It does not define tables or indexes. The contract returns course code
and name on browse and uses the spec sentences on enrollment. Routes
remain a mapping from use-case results to HTTP. Repository modules do
not import Flask. Design still passes Principles I through XV.

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
└── tasks.md              # /speckit-tasks, not created here
```

### Source Code (repository root)

Paths are relative to `lab-4/`.

```text
pyproject.toml
src/college/
├── domain/
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
    └── test_http_enrollment.py
```

**Structure Decision**: Single greenfield web service under
`src/college`. Domain modules have no Flask or `sqlite3` imports.
`student.py` holds the name, email, and programme reference invariants.
`course.py` holds the course-code and name invariants.
`browse_courses` and `enroll_student` depend on ports. `http.py` parses
JSON, calls one use case, and maps the result to the contract.
Outbound modules implement the ports and own persistence. `app.py` is
the composition root. `sqlite_unit_of_work.py` opens the transaction
for enrollment so a refusal cannot leave a partial write. Programme,
student, course, and inscription do not share domain modules.

The directory tree illustrates the split. Compliance is judged from
dependency direction and responsibility, not from file placement.

### Architectural obligations

**Permitted dependency direction**

- Domain types depend only on other domain types. They MUST NOT depend
  on application services, port implementations, inbound adapters,
  outbound adapters, Flask, or `sqlite3`.
- Application use cases depend on domain types and on the port
  interfaces they declare. They MUST NOT depend on an adapter
  implementation, Flask, or `sqlite3`.
- Inbound adapters depend on application use cases. They MUST NOT
  depend on outbound adapters.
- Outbound adapters depend on the port interfaces they implement and
  on the infrastructure those ports require. They MUST NOT depend on
  inbound adapters or on Flask.
- The composition root depends on use cases and on concrete adapters
  so it can construct the application. No other module may do that
  wiring.

**HTTP adapter and use case**

An HTTP adapter MAY parse and validate request structure, construct a
command or query, invoke one application use case, and translate that
use case's outcome into an HTTP status code and a response body.

An HTTP adapter MUST NOT independently determine enrollment
eligibility, student or course existence, or whether the business
operation succeeded or failed.

The HTTP presentation layer MAY own the response wording. That wording
MUST express the outcome the application layer already determined, and
it MUST preserve any exact outcome text the specification requires. It
MUST NOT introduce a new business decision.

An outbound adapter MUST NOT determine those outcomes and MUST NOT
choose the response wording.

**Uniqueness conflict**

The business layer owns the one-inscription rule. The database may
reject a concurrent duplicate as an atomic persistence guarantee.
That rejection does not move the rule into persistence. The adapter
exposes the persistence conflict and does not decide the business
outcome. The use case interprets that conflict as already enrolled.

**Cross-capability dependencies**

Each capability owns its own data.

- Programme owns the programme identifier.
- Student owns the student identifier, name, email address, and the
  programme identifier stored on the student.
- Course owns the course identifier, course code, and name.
- Inscription owns the inscription identifier, the student identifier,
  the course identifier, and the optional note.

The only permitted reference from one capability to another is an
identifier value on the owning record. A student may store a programme
identifier. An inscription may store a student identifier and a course
identifier. That value is not an imported entity. This rule does not
require or forbid a database foreign key. A foreign key is a storage
choice, not a domain dependency.

A use case may call one port for each capability it coordinates.
Enrollment may call the student, programme, course, and inscription
ports. Browse may call the course port. A port implementation MUST
read and write only the capability it serves.

These patterns are prohibited:

- A domain module importing another capability's domain module.
- A value object shared by two capabilities. An identifier that crosses
  a boundary is a plain value owned by the record that stores it.
- A repository reading or writing another capability's data.
- One use case calling another use case.

**Port-based interaction**

A use case reaches a student, course, programme, or inscription only
by calling a port. A port is an interface declared by the application.
The use case names the operation it needs. It does not name a
database, a driver, or an HTTP type.

**Dependency wiring**

Concrete adapters are constructed and bound to ports only in the
composition root. A test may bind a fake at that same boundary. A use
case module MUST NOT construct an adapter.

**Verification**

A review can fail the design without looking at directory names:

- A domain or application module that imports Flask, `sqlite3`, or an
  adapter implementation fails.
- An inbound adapter that imports an outbound adapter fails.
- An HTTP adapter that decides enrollment eligibility, student or
  course existence, or business success or failure on its own fails.
- An HTTP response whose wording states a different business outcome
  from the use case result fails.
- An outbound adapter that determines an enrollment outcome or chooses
  response wording fails.
- A use case that reads or writes a student, course, programme, or
  inscription other than through a port fails.
- A domain import across capabilities, a shared cross-capability value
  object, a repository that touches another capability's data, or a
  use case that calls another use case fails.
- Adapter construction outside the composition root, other than a test
  binding a fake, fails.

## Complexity Tracking

No constitution violation requires justification. Repository ports and
the unit-of-work boundary are required by Principles IX and X.
