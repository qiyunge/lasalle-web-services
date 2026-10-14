# Lab-4 College Management Constitution

The college management web service serves college administrative staff
who manage academic programmes, students, courses, and enrollments.
This constitution records that business context only.

## Core Principles

### I. Programme Membership

Every student MUST belong to an existing programme.

Rationale: A student is a learner registered in a programme. A student
record that names a missing programme is not a valid registration.

### II. Enrollment References

Every enrollment MUST reference an existing student and an existing
course.

Rationale: An inscription records one student's enrollment in one
course. Both the student and the course MUST already exist.

### III. Unique Course Enrollment

A student MUST NOT enroll in the same course more than once.

Rationale: One inscription is the sole record of that student in that
course. A second inscription for the same student and course is a
conflict.

### IV. Grade Within Permitted Range

An enrollment MAY exist without a grade. Any assigned grade MUST be
within the permitted range.

Rationale: A note is optional at enrollment time. When a note is
assigned, it shows that student's grade in that course, and a value
outside the permitted range is not a valid note. A feature that
assigns a note MUST state the permitted range it enforces.

### V. Explicit Failure

An operation that involves a nonexistent record or a conflicting
record MUST fail explicitly. It MUST NOT succeed silently.

Rationale: Administrative staff MUST be able to tell that the
operation did not take effect. Silent success would hide a missing
programme, student, or course, or a duplicate inscription.

## Domain Vocabulary

- **programme**: An academic programme offered by the college.
- **student**: A learner registered in a programme.
- **course**: A course offered by the college.
- **inscription**: A student's enrollment in a course.
- **note**: The grade associated with an enrollment. It shows a
  student's grade in a course.

## Feature Specification Requirements

Every feature specification MUST state:

- who the capability serves
- the expected business behaviour
- the failure paths, including the user-facing error messages
- what is explicitly out of scope

A specification that omits any of these items does not comply with
this constitution.

## Governance

This constitution is the business-context authority for lab-4 feature
specifications. It supersedes informal descriptions of programmes,
students, courses, inscriptions, and notes.

This constitution MUST stay limited to business context. It MUST NOT
define architecture, implementation technologies, data schemas, API
endpoint designs, or engineering practice.

An amendment MUST be written into this file, MUST state which
principle, vocabulary entry, or specification requirement changed, and
MUST update the version and last-amended date in the same change.

Versioning follows semantic versioning:

- MAJOR: remove or redefine an adopted business rule.
- MINOR: add a business rule, vocabulary entry, or specification
  requirement.
- PATCH: clarify wording without changing a rule.

Each feature specification MUST be checked against these principles
before it is accepted. The review MUST confirm the audience, the
expected behaviour, the failure paths and user-facing error messages,
and the explicit out-of-scope statement.

**Version**: 1.0.0 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-14
