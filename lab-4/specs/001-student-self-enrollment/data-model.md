# Data Model: Student Self-Enrollment

This slice reads programmes, students, and courses. It creates an
inscription only for the acting student. It does not register students,
create courses, or write grades.

The fields below are domain invariants from constitution 1.3.0 and the
feature spec. They are not a SQL schema, a table definition, an index,
or a repository implementation. Storage decisions are in
[research.md](research.md).

A text value is present when it is a non-empty string. Uniqueness
compares the stored value exactly.

## Programme

An academic programme offered by the college. This slice does not create
or edit programmes. It only checks that a student's programme exists.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. |

A programme has no relationship to a course in this slice.

## Student

A learner registered in a programme. This slice does not create or edit
students.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. |
| name | yes | Must be present. |
| email | yes | Must be present. Unique among students. |
| programme_id | yes | Must reference an existing programme. |

A student with no record, a missing name, a missing email address, or a
`programme_id` that does not reference a programme is not a registered
student for enrollment.

The student's programme does not restrict which courses can be browsed
or enrolled in. Two students must not share an email address. This
slice does not provide a way to create or change a student, so it does
not define a new failure message for a duplicate email.

## Course

A course offered by the college. This slice does not create or edit
courses. Every valid course can be browsed and is eligible for
self-enrollment.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. The inscription references this identifier. |
| course_code | yes | Must be present. Unique among courses. |
| name | yes | Must be present. Not required to be unique. |

A course with no record, a missing course code, or a missing name is
not an existing course for enrollment. No capacity, prerequisite,
availability, enrollment period, or programme link is part of this
slice.

## Inscription

One student's enrollment in one course.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. Assigned when the inscription is created. |
| student_id | yes | Must reference an existing registered student. On self-enrollment this is the acting student. |
| course_id | yes | Must reference an existing course. |
| note | no | Absent when this slice creates the inscription. This slice never writes a note. |

Uniqueness: at most one inscription for a given `(student_id, course_id)`.
The same course may have inscriptions for different students.

### Validation

- The acting student must be a registered student: present name, present
  email address, and an existing programme.
- The course must exist and have a present course code and a present
  name.
- The pair `(student_id, course_id)` must not already exist.
- The new inscription has no note.
- A request that names a different student creates nothing.
- A request that includes `note` creates nothing and changes no existing
  note.

### State

This slice has one transition: no inscription for that student and
course, then one inscription with no note.

It does not withdraw an inscription or write a note. A refused duplicate
leaves the existing inscription, including any note already stored,
unchanged. Any refused enrollment leaves every inscription unchanged.

## Relationships

```text
programme 1 --- * student
student    1 --- * inscription
course     1 --- * inscription
```

An inscription references one student and one course. A course does not
reference a programme. A note is the optional grade on an inscription,
not a separate record in this slice.

## Out of this model

- How a programme, student, or course record is created.
- How the acting student is authenticated.
- A permitted range or format for a staff-recorded note, an email
  address, or a course code beyond presence and exact uniqueness.
- Enrollment periods, capacity, prerequisites, and availability.
