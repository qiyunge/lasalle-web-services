# Constitution Prompt v1.3

Input for `/speckit-constitution`. This prompt adds project-wide domain invariants and updates the constitution to v1.3.0.

/speckit-constitution

Update the Lab-4 Constitution from version 1.2.0 to version 1.3.0.

This is a minor bump. It adds domain invariants. It does not remove or redefine an existing business principle or architectural constraint.

## Preservation

Preserve all existing business principles and all existing architecture principles.

Preserve the domain vocabulary and the feature-specification requirements.

Where an invariant below restates a rule already adopted, keep the adopted rule and record the added detail. Do not treat that restatement as a new conflicting rule.

## Domain Invariants

Add the following project-wide domain invariants.

### Student

A student has an identifier, a required name, a required email address, and a reference to an existing programme.

Student email addresses MUST be unique.

### Course

A course has an identifier, a required course code, and a required name.

Course codes MUST be unique. Course names are not required to be unique.

### Inscription

An inscription references an existing student and an existing course, and it MAY have no grade.

A student MUST NOT have more than one inscription for the same course.

## Limits

These are project-wide domain constraints, not implementation instructions.

Do not prescribe SQL schemas, table definitions, indexes, or repository implementations.

Do not modify application code or create a Git commit.
