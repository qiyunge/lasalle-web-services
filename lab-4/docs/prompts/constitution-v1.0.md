# Constitution Prompt v1.0

Input for `/speckit-constitution`. This prompt establishes business context only.

## Project

Build the business context for a college management web service (lab-4).

At this stage, record who the service serves, the business rules, the domain vocabulary, and what every feature specification must contain.

## Primary Users

College administrative staff responsible for managing:

- academic programmes
- students
- courses
- enrollments

## Business Rules

- Every student must belong to an existing programme.
- Every enrollment must reference an existing student and an existing course.
- A student cannot enroll in the same course more than once.
- An enrollment may exist without a grade. Any assigned grade must be within the permitted range.
- Operations that involve nonexistent or conflicting records must fail explicitly. They must not succeed silently.

## Domain Vocabulary

| Term | Definition |
| --- | --- |
| programme | An academic programme offered by the college. |
| student | A learner registered in a programme. |
| course | A course offered by the college. |
| inscription | A student's enrollment in a course. |
| note | The grade associated with an enrollment. It shows a student's grade in a course. |

## Feature Specification Requirements

Every feature specification must state:

- who the capability serves
- the expected business behaviour
- the failure paths, including user-facing error messages
- what is explicitly out of scope

## Limits of This Constitution

Keep this constitution to business context.

Leave the following unset:

- architecture
- implementation technologies
- data schemas
- API endpoint designs
- engineering practice

Do not modify application code. Do not create a Git commit.
