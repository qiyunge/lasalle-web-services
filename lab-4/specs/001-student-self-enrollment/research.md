# Research: Student Self-Enrollment

Lab 4 already contains this slice. Research uses the accepted
specification, constitution 2.0.4, and the current `lab-4/` code. The
shared Git repository also contains Lab 3. That tree was not read and
is not a design source.

## Existing service

**Decision**: Reuse the current `college` package. Do not add a second
application, a second persistence mechanism, or a parallel use case.

**Rationale**: Browse, self-enrollment, the FR-014 refusal order, the
SQLite uniqueness conflict, and the HTTP mapping already exist.
Constitution E2 and E3 require that established shape unless a rule is
unmet.

**Alternatives considered**: A new package or a rewrite of the ports.
Both would replace working boundaries without a demonstrated need.

## Web framework

**Decision**: Flask 3.1.3, with no Flask extensions.

**Rationale**: Constitution E1 requires Flask on Python 3.12.
`pyproject.toml` already pins Flask 3.1.3. The inbound adapter is the
only production module that imports Flask, apart from the composition
root.

**Alternatives considered**: Another framework, an unpinned Flask
install, or a Flask extension. E1 names Flask. An extension would add
infrastructure the current adapter does not need.

## Persistence

**Decision**: SQLite through the standard-library `sqlite3` module.
Outbound adapters implement the existing application ports. Domain
modules do not import `sqlite3`.

**Rationale**: E1 requires SQLite. `sqlite3` is already the runtime.
A5 keeps rows and connections inside the outbound adapters.

**Alternatives considered**: An ORM or a second database library. No
demonstrated need under E3.

## Tests and coverage

**Decision**: pytest and pytest-cov, as already configured.
`addopts` measure branch coverage of the `college` package and fail
under 100. Tests live in `tests/unit` and `tests/integration`. The
Flask test client covers HTTP. A separate curl run covers the running
process.

**Rationale**: Q2 requires pytest. Q4 requires branch coverage of new
or modified business code, checked from branch-level data, and requires
the overall result to stay at the baseline measured with this same
scope. The configured fail-under is the project gate. The constitutional
baseline remains that measured report, not a number copied into the
constitution.

**Alternatives considered**: `unittest`, or a new coverage package.
`unittest` conflicts with Q2. Another coverage tool would duplicate
pytest-cov.

## Layout and ports

**Decision**: Keep `src/college` split into `domain`, `application`,
and `adapters`, with `app.py` as the only production composition root.
`browse` and `enroll` are the driving use-case contracts.
`EnrollmentResult` is the enrollment outcome. Outbound capabilities stay
on `ProgrammePort`, `StudentPort`, `CoursePort`, `InscriptionPort`, and
`UnitOfWorkPort`.

**Rationale**: A1 requires a distinct domain and application. A3
requires application-owned use cases and outbound ports. The functions
already are the driving contracts, and only the inbound adapter calls
them. A Protocol with one implementation would add no boundary. A6
allows the application and the domain to share domain types.

**Alternatives considered**: New driving-port Protocols, or DTOs that
copy `Student`, `Course`, and `Inscription` inside the core. Neither
separates a boundary that the current types fail to separate.

## Boundary translation

**Decision**: Translate at the inbound and outbound edges only.

- The HTTP adapter turns a JSON object into `enroll` arguments and
  turns `EnrollmentResult` or the browsed courses into JSON. It maps
  `result.outcome` through the existing status table.
- Each SQLite repository turns a `sqlite3.Row` into a domain entity.
  `IntegrityError` becomes `PersistenceConflict` before it leaves the
  inscription repository.
- `Student`, `Course`, `Inscription`, and `EnrollmentResult` stay as
  they are inside the core.

**Rationale**: A4, A5, and A6 put translation where the representation
changes. A Flask request and a SQLite row stay outside the core.

**Alternatives considered**: Domain objects built in the route, or a
response DTO inside `enroll`. The route would own business data, and
the DTO would copy the outcome the use case already returns.

## Transport validation and business refusal

**Decision**: The inbound adapter owns request shape. The application
owns FR-014.

The adapter accepts a JSON object whose `acting_student_id` and
`course_id` are integers. `True` and `False` are not integers. A body
that is not an object is treated as an empty object. These failures
use the sentences the service already returns:

- `acting_student_id is required.`
- `course_id is required.`
- `acting_student_id and course_id must be integers.`

Those sentences are transport outcomes. They are not part of FR-014
and they are not authorization. The use-case precondition is that both
identifiers are integers. From there `enroll` applies only this order:
grade attempt, then enrolling someone else, then not a registered
student, then the course does not exist, then already enrolled.

A grade attempt is the first of those business rules. It is a
well-formed request whose `note` key is present, including when the
value is JSON null. The adapter's translation is `payload.get("note",
ABSENT)`. It does not drop a present key, it does not treat JSON null
as a missing field, and it does not choose the grade sentence. `enroll`
returns outcome `forbidden` with "Students cannot assign, change, or
remove a grade." The adapter maps that outcome to 400. The same status
number is used for a shape failure. The status is not the decision.

Inspection: the three shape checks and the grade check all still run
inside `enroll`. The grade check is already in the application and
already precedes the other-student check. The planned move is only the
three shape sentences. The grade check stays in `enroll`.

**Rationale**: The specification defines the five business refusals and
their messages. It does not define request-shape messages. A4 makes the
adapter translate the external request into the application input. B7
and FR-011 keep the grade decision in the application. The existing
sentences stay so the HTTP contract does not gain new wording.

**Alternatives considered**: Treating a present `note` as a shape
error. That would move authorization into the adapter. Inventing a new
business message for a missing field. Leaving the shape checks inside
`enroll`. The last keeps a transport decision in the use case.

## Identifiers and required text

**Decision**: Identifiers are integers. A name, an email address, a
course code, and a course name are present when the value is a string
and it contains at least one character. Uniqueness compares the stored
value exactly. This slice does not trim or case-fold text.

**Rationale**: The specification states that presence rule and declines
a trimming rule. B2 and B3 require uniqueness and do not define a
format.

**Alternatives considered**: A pattern for email or course code, or
case-insensitive email comparison. Neither is stated.

## Student and course records

**Decision**: This slice does not create or edit programmes, students,
or courses. Enrollment reads them. A registered student has an
identifier, a nonempty name, a nonempty email address, and an existing
programme. An existing course has an identifier, a nonempty course code,
and a nonempty name. Anything short of that uses the specification
sentence already adopted for that case: "Only a registered student can
enroll in a course." or "That course does not exist."

Email uniqueness and course-code uniqueness stay identity invariants.
This slice has no student or course write path, so it adds no duplicate
failure and no storage rule for those fields.

**Rationale**: B1, B2, and B3 define the records. The specification
maps incomplete records onto the existing sentences and puts catalogue
maintenance out of scope.

**Alternatives considered**: New sentences for a blank email or a
duplicate course code. Those messages are not in the specification.

## Domain invariant checks

**Decision**: A2 is resolved in the target design by domain factories
and by the dataclass constructors. `domain/result.py` holds `Success`,
`Failure`, and `ConstructionError`. `Student.create`, `Course.create`,
and `Inscription.create` return `Failure` for an invariant breach and
do not raise. The matching `Student(...)`, `Course(...)`,
`Inscription(...)`, and `Programme(...)` calls raise `ConstructionError`
and do not return an entity. `Programme` has no factory. The current
constructors do not implement this yet.

`InvalidStudent` and `InvalidCourse` carry the row identifier and no
user-facing sentence. `Missing` is the port value for no row. The
SQLite adapter calls the factory and returns that `Result`. It does
not choose the specification sentence. `enroll` maps a missing or
invalid student, and a missing programme, to the existing
not-registered sentence. It maps a missing or invalid course to the
existing missing-course sentence. FR-014 order is unchanged.

`list_all` returns `CourseList`: the valid courses and one
`InvalidCourse` for every row the factory refuses. The repository does
not drop those rows. `browse` keeps both parts. HTTP shows `courses`
only.

Email and course-code uniqueness stay collection rules without a write
path. Programme existence stays an application lookup. A restored
inscription note is not rejected for range. `Failure(InvalidInscription)`
is an internal integrity failure. Outcome `integrity` maps to HTTP 500
and "Stored inscription data is invalid." `enroll` calls `rollback`
and does not insert. That path is not an FR-014 refusal.

**Rationale**: A2 requires the owning model to enforce the invariant on
every public construction path. A7 requires the application to decide
what a missing or invalid record means. A5 keeps the row in the
adapter. Decision item 1 of this revision forbids exceptions for
expected validation and data recovery. Decision item 5 forbids a silent
skip in `list_all`.

**Alternatives considered**: Using `ConstructionError` for a row the
repository restored. Recovery stays on `Result`. The constructor raises
only when that public path is called with an invalid value. Leaving
`has_identity` as a report on an invalid entity. That does not enforce
construction. Skipping invalid courses inside the repository. That
drops the diagnostic before the application can see it. A second
field-for-field DTO. The port already returns the domain entity or the
domain failure. Adding `Programme.create`. A programme has no invalid
text, so the identifier check on `Programme(...)` is enough.

## Course browse

**Decision**: Browse shows every course the domain factory accepts.
Each shown item carries `id`, `course_code`, and `name`. The
application result also keeps `InvalidCourse` diagnostics from
`CourseList`. Those diagnostics are not a field of `GET /courses`.
The list is not filtered by programme or by an existing inscription.
The current sort by `course_code` stays presentation for the valid
courses. The specification requires the set, and it states that
display order is not a business rule.

**Rationale**: FR-001 through FR-003 and the browse scenarios define
the set and the fields. The out-of-scope list excludes order. The
current sort remains because E2 says to reuse the implementation.
Existing tests that lock the sort stay. They are narrower than the
specification allows, and this plan does not remove them.

**Alternatives considered**: Treating the sort as a specification rule,
or changing the order. The specification excludes the first. The second
would change current behavior for no business requirement.

## Acting student

**Decision**: `POST /inscriptions` carries `acting_student_id`. The
service does not define login, sessions, or tokens. `GET /courses`
does not take a student identifier.

**Rationale**: The specification says recognition is out of scope and
that browse shows every existing course.

**Alternatives considered**: A session or an authentication header.
That would specify the recognition mechanism the specification excludes.

## Grade attempts and enrollment target

**Decision**: Omitting `note` is the successful enrollment, and the
created inscription has no grade. A present `note` key, including JSON
null, is application authorization: the first FR-014 rule. It is not a
request-shape failure. Omitting `student_id`, or sending the acting
student's own id, enrolls the acting student. A different `student_id`
is an attempt to enroll someone else, decided by `enroll`. The course
is selected by `course_id`.

**Rationale**: The specification requires those two refusals and a
grade-free inscription. It does not define the JSON encoding. The
current contract is the encoding this service already uses. The adapter
preserves key presence. The use case chooses the sentence.

**Alternatives considered**: A separate grade route, or enrollment by
course code. The first is grade management. The second adds a key the
inscription does not use.

## Refusal precedence

**Decision**: Business precedence is the clarified FR-014 order. The
first match wins, and the attempt writes nothing. Transport shape is
decided before `enroll` and is not ranked against those five rules.

**Rationale**: The 2026-10-15 clarification fixed the business order.
The specification does not rank transport failures among those rules.
An unusable identifier never becomes a business attempt.

**Alternatives considered**: A combined message, or ranking a missing
field inside FR-014. The clarification chose one message. The
specification does not list the shape checks as business rules.

## HTTP status mapping

**Decision**: Keep the current outcome map.

| Outcome | Status |
| --- | --- |
| Course list, including an empty list | 200 |
| Inscription created | 201 |
| Missing or non-integer required field | 400 |
| Grade attempt | 400 |
| Enrollment for another student | 400 |
| Person is not a registered student | 400 |
| Course does not exist | 404 |
| Already enrolled | 409 |
| Stored inscription cannot be constructed | 500 |

The 201 body includes the created inscription: `id`, `student_id`,
`course_id`, and `note: null`. There is no inscriptions list.

**Rationale**: The specification fixes the business sentences and the
persisted inscription. It does not fix status codes. The current map
distinguishes creation, a missing course, and a conflicting
inscription. The 500 outcome is an integrity failure, not one of those
business results. Its message is defined by this contract and is not
added to the specification. The 201 body makes the new inscription
observable. SC-001 does not add a read endpoint. A later duplicate
refusal observes that the same inscription persisted.

**Alternatives considered**: 403 for authority refusals, or a list of
inscriptions. 403 implies an authentication scheme this feature does
not have. A list is out of scope.

## Transaction and uniqueness

**Decision**: Keep one enrollment transaction on one connection.

`enroll` opens `unit_of_work`, loads the student, programme, and course,
looks for an inscription, and inserts only when every business check
passes. `SqliteUnitOfWork` runs `BEGIN IMMEDIATE`, commits when the
block finishes, and rolls back when it raises. `PersistenceConflict` is
handled outside that block, so the rollback runs before the use case
maps the conflict to "You are already enrolled in this course."

The business layer owns the one-inscription rule and checks it before
insert. `UNIQUE (student_id, course_id)` is the existing atomic
guarantee for overlapping attempts. The repository translates
`IntegrityError` into `PersistenceConflict` and does not choose the
message. The use case does.

Browse uses a separate read connection and does not start this write
transaction.

Email and course-code uniqueness are not given a new write path or a
new storage constraint in this slice.

**Rationale**: A7 requires the use case to preserve the invariant across
the write, and requires the adapter to report the persistence fact
without making the business decision. B4 is the one-inscription rule.
The current unique pair is what makes the overlapping case atomic.

**Alternatives considered**: Catching `IntegrityError` in the use case,
checking the duplicate only in SQLite, or adding email and course-code
indexes. The first leaks a SQLite error into the core. The second hides
the business rule in the adapter. The third is storage design for
records this feature does not write.

## Static checks

**Decision**: Do not add a linter or a type checker.

**Rationale**: None is configured. Q3 says that the principle adds no
tool, and that a missing tool means there is no configured check to
run. E3 still requires a demonstrated need before a new dependency.
The planning request asked for both checks. That request does not amend
Q3.

**Alternatives considered**: Adding Ruff or mypy in this plan. Either
would be a new dependency chosen without a project decision.

## Running verification

**Decision**: pytest is the planned automated gate. curl against the
running service is the planned HTTP gate. A 201 body followed by the
already-enrolled refusal is the planned SC-001 persistence check. No
permanent per-cycle log is required.

On 2026-10-15 this review executed pytest with branch coverage: 46
passed, 30 branches, 0 missing, plus a warning that module `college`
was previously imported and not measured. That run is not the Q4
baseline. Curl was not executed in this review. Q4 and Q5 are not
passed.

**Rationale**: Q5 separates curl from the Flask test client. Q6 makes
the completion report the evidence. E5 requires Red and Green to be
seen during execution when behavior changes, and existing tests before
and after when behavior stays.

**Alternatives considered**: Treating the test client as the HTTP gate,
or storing a log file per cycle. Q5 declines the first. Q6 declines the
second unless a request asks for a file.
