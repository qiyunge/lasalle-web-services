<!--
Sync Impact Report
- Version change: 1.2.0 → 1.3.0
- Modified principles (rules kept; added detail only):
  - I. Programme Membership
  - II. Enrollment References
  - III. Unique Course Enrollment
  - IV. Grade Within Permitted Range
- Added principles:
  - XIV. Student Identity
  - XV. Course Identity
- Added sections: none
- Removed sections: none
- Vocabulary: student and course entries expanded. programme,
  inscription, and note unchanged.
- Governance: domain invariants are business rules, not SQL schemas,
  table definitions, indexes, or repository implementations.
- Follow-up TODOs: none
-->

# Lab-4 College Management Constitution

The college management web service serves college administrative staff
who manage academic programmes, students, courses, and enrollments.
Students are also primary users. A student may browse available courses
and enroll in a course without administrative intervention.
The service is built with Python 3.12, Flask, and SQLite.
This constitution records that business context, the project-wide
domain invariants, and the architectural constraints that govern the
service.

## Core Principles

### I. Programme Membership

Every student MUST belong to an existing programme.

The student's reference to an existing programme is this rule. The
student's identifier, required name, and required email address are
Principle XIV. They do not replace this membership rule.

Rationale: A student is a learner registered in a programme. A student
record that names a missing programme is not a valid registration.

### II. Enrollment References

Every enrollment MUST reference an existing student and an existing
course.

An inscription is that enrollment and MUST reference an existing
student and an existing course. This is the same rule, stated as a
project-wide domain invariant. It does not prescribe a SQL schema, a
table definition, an index, or a repository implementation.

Rationale: An inscription records one student's enrollment in one
course. Both the student and the course MUST already exist.

### III. Unique Course Enrollment

A student MUST NOT enroll in the same course more than once.

A student MUST NOT have more than one inscription for the same course.
This is the same rule, not a second limit.

Rationale: One inscription is the sole record of that student in that
course. A second inscription for the same student and course is a
conflict.

### IV. Grade Within Permitted Range

An enrollment MAY exist without a grade. Any assigned grade MUST be
within the permitted range.

An inscription MAY have no grade. This is the same rule.

Rationale: A note is optional at enrollment time. When a note is
assigned, it shows that student's grade in that course, and a value
outside the permitted range is not a valid note. A feature that
assigns a note MUST state the permitted range it enforces.

### V. Explicit Failure

An operation that involves a nonexistent record or a conflicting
record MUST fail explicitly. It MUST NOT succeed silently.

Rationale: Administrative staff and students MUST be able to tell that
the operation did not take effect. Silent success would hide a missing
programme, student, or course, or a duplicate inscription.

### VI. Student Self-Enrollment

A student MAY browse available courses. A student MAY enroll in a
course without administrative intervention.

A grade is not required at enrollment time. All applicable enrollment
business rules remain in force.

Rationale: Students are primary users. Browsing courses and creating
the student's own inscription are actions the student may perform
directly. An administrator is not required to complete either action.
The inscription still has to satisfy every enrollment rule already
adopted. Principle IV already allows an enrollment with no grade.

### VII. Student Enrollment Authority

A student MUST NOT create or modify an enrollment on behalf of another
student.

A student MUST NOT assign, modify, or remove a grade, including a grade
associated with that student's own enrollment. Grade management is
reserved for authorized college staff.

This constitution does not grant a student the ability to withdraw from
a course. That capability has not been specified.

Rationale: Student authority covers browsing available courses and
enrolling oneself. It does not cover another student's inscription, and
it does not include assigning, changing, or removing a note. Leaving a
course is a separate business rule that has not been adopted.

### VIII. Technology Stack

The college management web service MUST be built with Python 3.12,
Flask, and SQLite.

Rationale: These are the adopted implementation technologies. Replacing
the language, the web framework, or the database is a new
infrastructure choice and requires a demonstrated need.

### IX. Hexagonal Architecture

The system MUST follow hexagonal architecture.

- Domain rules MUST remain independent of frameworks and
  infrastructure.
- Application use cases MUST coordinate business operations through
  explicit ports.
- Inbound adapters MUST translate external requests into application
  commands or queries.
- Outbound adapters MUST implement persistence and other
  infrastructure concerns.

Rationale: Business rules stay testable without Flask or SQLite. Ports
are the only path by which a use case reaches anything outside the
application.

### X. Thin Adapters

HTTP routes MUST stay thin. Business rules MUST NOT be implemented in
Flask routes or SQLite adapters. Persistence access MUST go through
repository ports. Transaction boundaries MUST preserve domain
invariants.

Rationale: A route or a SQLite adapter that contains a business rule
binds that rule to the framework. A transaction that breaks an
invariant would persist an invalid domain state.

### XI. Capability Boundaries

The student, course, programme, and inscription capabilities MUST stay
clearly bounded. A feature's design MUST respect those existing
boundaries and MUST NOT introduce unnecessary coupling between them.

Rationale: Each capability has its own business rules. Coupling them
without need makes a change in one capability a change in another.

### XII. Established Conventions

Work MUST follow the conventions already present in the project.
External dependencies MUST remain minimal. A new architectural
pattern, framework, or infrastructure component MUST NOT be introduced
without a demonstrated need.

Rationale: The project already has an adopted shape. An extra pattern
or dependency is justified only when that shape cannot meet the need.

### XIII. Architect Clarification

A design question that these constraints do not settle MUST be
clarified with the architect. It MUST NOT be decided autonomously.

Rationale: These principles fix the boundaries that are already
adopted. A question they leave open is an architect decision.

### XIV. Student Identity

A student MUST have an identifier, a name, and an email address. The
name MUST be present. The email address MUST be present. The student
MUST reference an existing programme, as Principle I requires.

Student email addresses MUST be unique.

These are domain invariants. They MUST NOT be read as a SQL schema, a
table definition, an index, or a repository implementation.

Rationale: A student without a name or an email address is not a
complete registration. Two students MUST NOT share an email address.
The programme reference remains the membership rule in Principle I.

### XV. Course Identity

A course MUST have an identifier, a course code, and a name. The course
code MUST be present. The name MUST be present.

Course codes MUST be unique. Course names are NOT required to be unique.

These are domain invariants. They MUST NOT be read as a SQL schema, a
table definition, an index, or a repository implementation.

Rationale: The course code distinguishes one course from another. The
name is required so the course can be recognized. Two courses MAY share
a name when their codes differ.

## Domain Vocabulary

- **programme**: An academic programme offered by the college.
- **student**: A learner registered in a programme. A student has an
  identifier, a required name, a required email address, and a
  reference to an existing programme. Email addresses are unique.
- **course**: A course offered by the college. A course has an
  identifier, a required course code, and a required name. Course
  codes are unique. Course names are not required to be unique.
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

This constitution is the authority for lab-4 business context and for
the architectural constraints recorded in this file. It supersedes
informal descriptions of programmes, students, courses, inscriptions,
notes, and of how the service is structured.

Business principles, domain vocabulary, and feature-specification
requirements remain in force. This constitution records the
architecture, implementation technologies, and engineering constraints
named in Principles VIII through XIII. It MUST NOT define data schemas
or API endpoint designs.

The domain invariants in Principles I through IV, XIV, and XV are
business rules about students, courses, and inscriptions. They are not
implementation instructions. They MUST NOT be treated as SQL schemas,
table definitions, indexes, or repository implementations.

An amendment MUST be written into this file, MUST state which
principle, vocabulary entry, specification requirement, or
architectural constraint changed, and MUST update the version and
last-amended date in the same change.

Versioning follows semantic versioning:

- MAJOR: remove or redefine an adopted business rule or an adopted
  architectural constraint.
- MINOR: add a business rule, domain invariant, architectural
  constraint, vocabulary entry, or specification requirement.
- PATCH: clarify wording without changing a rule.

Each feature specification MUST be checked against the business
principles before it is accepted. The review MUST confirm the
audience, the expected behaviour, the failure paths and user-facing
error messages, and the explicit out-of-scope statement.

Each design and implementation change MUST be checked against
Principles VIII through XIII before it is accepted. The same review
MUST confirm that the domain invariants in Principles I through IV,
XIV, and XV still hold.

**Version**: 1.3.0 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-14
