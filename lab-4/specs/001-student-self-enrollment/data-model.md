# Data Model: Student Self-Enrollment

This slice reads programmes, students, and courses. It creates an
inscription only for the acting student. It does not register students,
create courses, or write grades.

The fields below come from constitution 2.0.4 principles B1 through B7
and from the accepted specification. They are domain facts. Storage
mechanics are in [research.md](research.md). The HTTP shape is in
[contracts/student-self-enrollment.md](contracts/student-self-enrollment.md).

A text value is present when it is a string of at least one character.
This feature does not define trimming. Uniqueness compares the stored
value exactly.

## Programme

An academic programme offered by the college. This slice does not create
or edit programmes. Enrollment checks that the student's programme
exists.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. |

A programme has no relationship to a course in this slice. It does not
filter browse or enrollment.

## Student

A learner registered in a programme. This slice does not create or edit
students.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. |
| name | yes | Nonempty. |
| email | yes | Nonempty. Unique among students. |
| programme_id | yes | References an existing programme. |

`Student.create` is the public construction path. It returns `Success`
only when the name and the email are nonempty. Otherwise it returns
`Failure(InvalidStudent)` and no entity. A missing student row, an
`InvalidStudent`, or a `programme_id` that does not reference a
programme means the person is not a registered student. The application
chooses that outcome. The factory does not.

The student's programme does not restrict which courses can be browsed
or enrolled in. This slice does not create students, so it does not
define a new failure for a duplicate email and does not compare emails
beyond the stored value.

## Course

A course offered by the college. This slice does not create or edit
courses. Every existing course can be browsed and is eligible for
self-enrollment.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. The inscription references this identifier. |
| course_code | yes | Nonempty. Unique among courses. |
| name | yes | Nonempty. Not required to be unique. |

`Course.create` is the public construction path. It returns `Success`
only when the course code and the name are nonempty. Otherwise it
returns `Failure(InvalidCourse)` and no entity. A missing course row
or an `InvalidCourse` does not exist for enrollment. Browse shows the
valid courses and retains each `InvalidCourse` on the course batch.

No capacity, prerequisite, availability, enrollment period, or programme
link belongs to this course.

## Inscription

One student's enrollment in one course.

| Field | Required | Rules |
| --- | --- | --- |
| id | yes | Identifier. Assigned when the inscription is created. |
| student_id | yes | The acting student on a successful self-enrollment. |
| course_id | yes | The chosen existing course. |
| note | no | Absent on an inscription this slice creates. This slice never writes a note. |

Uniqueness: at most one inscription for a given `(student_id, course_id)`.
The same course may have one inscription for each student.

### Business validation

`enroll` applies the first matching rule and stops.

1. A grade attempt. Message: "Students cannot assign, change, or remove a grade."
2. An attempt to enroll someone else. Message: "You can only enroll yourself."
3. The acting person is not a registered student. Message: "Only a registered student can enroll in a course."
4. The course does not exist. Message: "That course does not exist."
5. That student already has an inscription for that course. Message: "You are already enrolled in this course."

Request-shape checks are not rules of this model. They are translated
before the use case, as recorded in [research.md](research.md). A
present grade is rule 1 of the list above. It is application
authorization, including when the supplied grade value is empty.

`Student`, `Course`, and `Inscription` are constructed with `create`,
which returns `Result`, and with the dataclass constructor, which
raises `ConstructionError` for the same invariant. Neither path returns
an invalid entity. `Programme` is constructed only with `Programme(id)`
and rejects a non-integer id. Details are in [plan.md](plan.md).

The business messages and the order above stay as specified. A missing
student or course and an invalid restored student or course are
different `Result` failures. `enroll` maps both student failures to the
not-registered sentence and both course failures to the missing-course
sentence. `Failure(InvalidInscription)` is not one of those outcomes.
It is an integrity failure: no new inscription, the transaction rolls
back, and the HTTP contract uses status 500. Programme existence
remains an application check. Email and course-code uniqueness have no
write operation in this model. A course batch keeps invalid course
diagnostics. The HTTP course list does not gain a field for them.

A successful enrollment creates one inscription for the acting student
and the chosen course, with no note, and tells the student
"You are enrolled in this course."

### State

This slice has one transition: no inscription for that student and
course, then one inscription with no note.

A refused attempt does not create an inscription and does not change an
existing one. A refused duplicate leaves the stored note as it was,
including a note that staff recorded earlier. Withdrawal and grade
changes are not transitions of this slice.

Overlapping attempts for the same student and course end as one
inscription. The attempt that does not create it receives the
already-enrolled outcome.

## Relationships

```text
programme 1 --- * student
student    1 --- * inscription
course     1 --- * inscription
```

An inscription references one student and one course by identifier. A
course does not reference a programme. A note is the optional grade on
an inscription, not a separate record in this slice.

## Out of this model

- How a programme, student, or course record is created.
- How the acting student is recognized.
- A permitted range for a grade. This feature never assigns one.
- A new comparison rule or repair for duplicate student emails.
- Enrollment periods, capacity, prerequisites, and availability.
- The order in which courses are shown.
