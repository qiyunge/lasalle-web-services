# Student Enrollment Specification Prompt v1

Input for `/speckit-specify`. This prompt specifies the first feature slice only.

## Slice

Specify the first slice of the college management web service: a student browses available courses and enrolls in a course without administrative intervention.

## Authority

- The enrollment belongs to the acting student.
- A student must not create or modify an enrollment on behalf of another student.
- A student must not assign or modify grades, including a grade on their own enrollment.

Follow the existing project constitution. Use its domain vocabulary and satisfy its feature-specification requirements: who the capability serves, the expected business behaviour, the failure paths including user-facing error messages, and what is explicitly out of scope.

## Clarification

Ask clarifying questions one at a time before drafting the specification. Do not draft until those scope questions are answered.

## Limits

- Do not modify application code.
- Do not stage files or create a Git commit.
- Do not introduce architecture, authentication mechanisms, API designs, or implementation details.
