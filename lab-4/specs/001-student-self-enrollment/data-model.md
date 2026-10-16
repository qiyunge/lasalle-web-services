# Data Model: Student Self-Enrollment

Date: 2026-10-16

Business rules below are copied from the accepted specification. They
are not new rules. Field checks that are only about forming a command
are marked as input validation.

## Application input contract

An enrollment request before validation. Values may be unvalidated
primitives. It contains no transport object. It does not record an
authorization decision.

| Field | Presence | Before validation |
| --- | --- | --- |
| acting_student_id | required to form a command | Supplied by the trusted caller context. May be missing or not an integer. |
| course_id | required to form a command | May be missing or not an integer. |
| target student | not accepted | Absent, or any received value. A value that differs from the acting student names someone else. It does not select the inscription's student. |
| note | optional | Absent, or any received value, including null. |

The target student and `note` stay on this contract as unvalidated
facts. The use case reads them for FR-014. They are not copied into
the validated command. Authentication of the caller context is outside
this feature.

Independent failures for the two required identifiers are collected
together as typed errors with stable codes. They do not produce a
domain object. More than one of those failures uses the HTTP body in
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md).

## Validated enrollment command

Built only when both required identifiers are domain types. It contains
validated domain types only.

| Field | Type | Meaning |
| --- | --- | --- |
| acting_student_id | student identifier | The known acting student. |
| course_id | course identifier | The course named by the attempt. |

Domain behavior accepts this command. It does not receive the raw
contract, an unvalidated `student_id`, or `note`.

## Entity attributes

The accepted specification gives an identifier and a nonempty name to
Programme, Student, and Course. It does not give a name to
Inscription.

| Entity | Identifier | Name |
| --- | --- | --- |
| Programme | `id`, required. A student refers to it. | Required. Nonempty. Not required to be unique. |
| Student | `id`, required. | Required. Nonempty. |
| Course | `id`, required. | Required. Nonempty. May repeat. |
| Inscription | `id`, assigned when the inscription is stored. | Not an accepted attribute. |

## Programme

An academic programme. This slice does not create or change one.

| Field | Rule from the specification |
| --- | --- |
| id | Required identifier. A registered student refers to an existing programme. |
| name | Required. Nonempty. Not required to be unique. |

A programme record that lacks an identifier or a nonempty name is not
an existing programme. The programme does not choose which courses can
be browsed or joined. This slice does not create programmes.

## Student

A learner registered in a programme. This slice does not register
students.

| Field | Rule from the specification |
| --- | --- |
| id | Required identifier. |
| name | Required. Nonempty. |
| email | Required. Nonempty. Unique among students. |
| programme_id | Required. Refers to an existing programme, one with an identifier and a nonempty name. |

A person who lacks any of these is not a registered student. The
enrollment sentence is "Only a registered student can enroll in a
course." This slice does not define a separate sentence for a
duplicate email.

Construction of a `Student` fails closed. An invalid instance is not
returned.

## Course

A course offered by the college. This slice does not create courses.

| Field | Rule from the specification |
| --- | --- |
| id | Required identifier. |
| course_code | Required. Nonempty. Unique. |
| name | Required. Nonempty. May repeat. |

A record with no code or no name is not an existing course. It is not
shown in the browse list. Enrollment in it uses "That course does not
exist."

## Inscription

One student's enrollment in one course.

| Field | Rule from the specification |
| --- | --- |
| id | Identifier assigned when the inscription is stored. |
| student_id | The acting student on a successful self-enrollment. |
| course_id | The chosen existing course. |
| note | Absent on an inscription this slice creates. |

At most one inscription exists for a student and a course. A second
attempt does not create another and does not change a note already
stored. The sentence is "You are already enrolled in this course."

Two attempts that overlap still leave one inscription.

## Relationships

- A student belongs to one existing programme.
- An inscription refers to one registered student and one existing course.
- Browse returns existing courses only. It does not return inscriptions.

## State

An inscription created here has no grade. This slice has no withdrawal
and no grade change. A refusal does not change stored inscriptions.

## Not in this model

- Enrollment period, capacity, prerequisite, or availability status.
- A numerical grade range.
- How the caller learned the acting student.
