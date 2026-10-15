# Research: Student Self-Enrollment

Lab 4 is greenfield. This research uses the feature spec and Lab 4
constitution 1.3.0 only. The shared Git repository also contains Lab 3;
that tree was not read and is not a design source.

## Greenfield boundary

**Decision**: Plan this slice from `lab-4/` only.

**Rationale**: Lab 4 shares a Git repository with Lab 3, but it is a new
service. Lab 3 conventions are not Lab 4 conventions.

**Alternatives considered**: Reusing Lab 3 routes, schema, or packages.
Rejected because that would import another lab's design.

## Web framework

**Decision**: Flask 3.1.3, with no Flask extensions.

**Rationale**: The constitution requires Flask on Python 3.12. Flask
3.1.3 (released 2026-02-18) is the current stable release and supports
Python 3.9 and newer, including 3.12. Flask 3.2.0 is not a stable
release. Extensions such as Flask-SQLAlchemy would add a framework
between the application and SQLite.

**Alternatives considered**: An unpinned Flask install, the unreleased
3.2 line, or another web framework. The constitution names Flask, and
an unpinned install can move without a decision.

## Persistence

**Decision**: SQLite through the Python 3.12 standard-library `sqlite3`
module. Repositories are the only persistence port. No ORM. Domain
invariants stay in the domain and application layers. The adapter
stores and loads values; it does not define the invariants and it does
not choose user-facing sentences.

**Rationale**: The constitution requires SQLite and forbids business
rules inside SQLite adapters. `sqlite3` is already in the runtime.
Principles XIV and XV are domain rules, not table definitions or
indexes.

**Alternatives considered**: SQLAlchemy or Flask-SQLAlchemy. Both are
new infrastructure without a demonstrated need.

## Tests

**Decision**: pytest. Integration tests use Flask's test client and an
in-memory SQLite database. Branch coverage is measured with pytest-cov.

**Rationale**: Constitution Principle XVII requires pytest. That
requirement is the demonstrated need for this test dependency under
Principle XII. The slice needs automated proof of the acceptance
scenarios. Flask's test client is part of the required web framework.

**Alternatives considered**: `unittest` from the standard library. It
adds no dependency, and it conflicts with Principle XVII.

## Layout

**Decision**: One Python package, `college`, in a `src` layout, split
into `domain`, `application`, and `adapters`. Student, course,
programme, and inscription each keep their own domain module and their
own SQLite repository. Browse and enrollment use cases call ports.
Flask routes live in one inbound adapter. `app.py` wires the concrete
adapters.

**Rationale**: The constitution requires hexagonal architecture,
explicit ports, thin HTTP routes, and separate capabilities. Lab 4 has
no existing application tree.

**Alternatives considered**: A flat `models/` and `services/` tree, or
modules that import Flask and `sqlite3` directly. Both would place
business rules next to the framework or the database.

## Identifiers and required text

**Decision**: Identifiers are integers assigned by SQLite. A name, an
email address, a course code, and a course name are present only when
the stored value is a non-empty string. Email uniqueness and course-code
uniqueness compare the stored value exactly. This slice does not trim,
case-fold, or define a further email or course-code format.

**Rationale**: The constitution requires those values and their
uniqueness. It does not define a string format or a normalization
rule. Exact match is the uniqueness rule without an extra policy.

**Alternatives considered**: UUIDs, a required email pattern, or
case-insensitive email uniqueness. None of those is stated in the
constitution or the spec.

## Student and course records

**Decision**: This slice does not create or edit programmes, students,
or courses. A student used for enrollment must already have an
identifier, a present name, a present email address, and a reference to
an existing programme. A course that is browsed or enrolled in must
already have an identifier, a present course code, and a present name.
Two stored students must not share an email address. Two stored courses
must not share a course code. Course names may be the same.

A student row that is missing, or whose name, email, or programme is
missing, is not a registered student. Enrollment then fails with
"Only a registered student can enroll in a course." A course row that
is missing, or whose course code or name is missing, is not an existing
course. Enrollment then fails with "That course does not exist."

**Rationale**: Constitution Principles I, XIV, and XV define a complete
student and a complete course. The spec already uses those two
sentences for an unregistered person and a missing course, and it does
not add a new sentence for an incomplete record. The spec also leaves
creating and maintaining students and courses out of scope, so this
slice only reads records that already satisfy the invariants.

**Alternatives considered**: New error sentences for a blank email or a
duplicate course code. That would add messages the spec does not state.
A maintenance API for students and courses would implement work the
spec puts out of scope.

## Course browse payload

**Decision**: Each browsed course includes its identifier, course code,
and name. The list is ordered by course code ascending. An empty
catalogue returns an empty list. The list is not filtered by programme
or by an existing inscription.

**Rationale**: Principle XV says a course has those three values, and
the name is what makes the course recognizable. The spec requires every
existing course to be shown. Ordering by the unique course code makes
the list stable.

**Alternatives considered**: Returning only the identifier. That would
hide the course code and name the constitution requires. Filtering by
the student's programme would violate the spec.

## Acting student

**Decision**: Enrollment requests carry `acting_student_id`. The service
does not define login, sessions, or tokens. Browse does not take a
student identifier and does not filter the catalogue.

**Rationale**: The spec says the acting student is already known and
that recognition is out of scope. Enrollment must still know who is
acting. Browse defines no failure message for an unknown caller, and
visibility does not depend on the student.

**Alternatives considered**: A session cookie or an authentication
header. That would design the recognition mechanism the spec leaves
out.

## Grade attempts

**Decision**: Omitting `note` creates an inscription with no grade.
Sending the `note` key, with any value including null, is an attempt to
assign, change, or remove a grade. The attempt is refused, and nothing
is written.

**Rationale**: This slice has no grade-management operation. A present
key is the attempt. A missing key is the success case required by the
spec and by Principle IV.

**Alternatives considered**: A grade route that only refuses, or
treating JSON null as a successful enrollment. The first looks like
grade management. The second hides an explicit removal attempt.

## Enrollment target

**Decision**: The inscription is for `acting_student_id` unless the body
also includes `student_id`. The same `student_id` as the acting student
is still self-enrollment. A different `student_id` is refused with
"You can only enroll yourself." and writes nothing. The course is
chosen by `course_id`, which is the course identifier. The course code
is displayed on browse; it is not a second enrollment key.

**Rationale**: The spec requires a testable refusal when the acting
student names someone else. The inscription references the course
identifier. The course code remains the unique code from Principle XV.

**Alternatives considered**: Enrolling by course code instead of course
id. The constitution gives the course both an identifier and a code.
The inscription rule references the course, and the request already
uses the identifier.

## Refusal order

**Decision**: Apply the first matching refusal and stop.

1. `acting_student_id` or `course_id` is missing or not an integer.
2. `note` is present.
3. `student_id` is present and differs from `acting_student_id`.
4. The acting student is missing, the name is missing, the email
   address is missing, or the student's programme is missing.
5. The course is missing, the course code is missing, or the course
   name is missing.
6. An inscription already exists for that student and course.

Missing required fields use "acting_student_id is required.",
"course_id is required.", or "acting_student_id and course_id must be
integers." Those are contract errors, not spec business sentences.
Later refusals use the exact spec sentences.

Programme mismatch with a course is not a failure. This slice stores no
enrollment period, capacity, prerequisite, or availability.

**Rationale**: The spec states each sentence and does not state which
sentence wins when one request matches more than one rule. One fixed
order is testable. Incomplete students and courses use the spec
sentences already adopted for "not registered" and "course does not
exist."

**Alternatives considered**: Leaving the winner unspecified, or
inventing a combined message.

## HTTP status mapping

**Decision**:

| Outcome | Status |
| --- | --- |
| Course list, including an empty list | 200 |
| Inscription created | 201 |
| Missing or non-integer required field | 400 |
| Grade attempt | 400 |
| Enrollment for another student | 400 |
| Acting person is not a registered student | 400 |
| Course does not exist | 404 |
| Already enrolled | 409 |

Success enrollment returns the created inscription: its id, student id,
course id, and `note: null`. There is no endpoint that lists a
student's inscriptions.

**Rationale**: The spec fixes the sentences and does not fix status
codes. 201 distinguishes creation from the course list. 404 and 409
distinguish a missing course from a conflicting inscription. The other
refusals share 400 because this slice has no authentication scheme.
Returning the created inscription lets the success scenario be checked
without a read API the spec places out of scope.

**Alternatives considered**: 403 for the authority refusals. 403
suggests an authentication scheme this slice does not have.

## Transaction and uniqueness

**Decision**: The uniqueness rule has three separate duties.

- The business layer owns the rule. A student MUST NOT have more than
  one inscription for the same course. The application use case checks
  that rule before it asks persistence to insert.
- The database provides an atomic persistence guarantee against a
  concurrent duplicate. Rolling back a conflicting insert does not
  move the business rule into the adapter, and it does not define the
  rule as a schema, an index, or a repository policy.
- The application interprets a recognized persistence conflict. The
  adapter exposes that conflict and does not decide the business
  outcome. The use case maps it to the already-enrolled result.

Creating an inscription runs in one SQLite transaction: load the acting
student and programme, load the course, look for an existing
inscription, then insert. Any refusal rolls back. If a concurrent
insert conflicts, the transaction rolls back, the adapter reports the
persistence conflict, and the use case applies the already-enrolled
result. The prior inscription, including any stored note, stays
unchanged.

Email uniqueness and course-code uniqueness are domain invariants on
records this slice does not create. This slice does not add a write
path, a table definition, or an index prescription for them.

**Rationale**: Principle X requires the transaction to preserve
invariants. Principle III is the one-inscription rule. Principles XIV
and XV forbid treating those identity rules as storage design, and the
spec leaves student and course maintenance out of scope.

**Alternatives considered**: Implementing email and course-code
uniqueness as SQL indexes in this slice, or checking the duplicate
inscription only inside the SQLite adapter. The first is a storage
design for data this slice does not write. The second would place the
business rule in the adapter.
