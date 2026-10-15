# Constitution Prompt v1.4

Input for `/speckit-constitution`. This prompt adds project-wide engineering and quality constraints and updates the constitution to v1.4.0.

/speckit-constitution

Update the Lab-4 Constitution from version 1.3.0 to version 1.4.0.

This is a minor bump. It adds engineering and quality constraints. It does not remove or redefine an existing business principle, domain invariant, or architectural constraint.

Replace the Sync Impact Report at the top of the constitution so it describes this amendment.

## Preservation

Preserve all existing business principles, domain invariants, and architecture principles.

Preserve the domain vocabulary and the feature-specification requirements.

Adopting pytest is an explicit engineering requirement. It is the demonstrated need for that test dependency. It does not remove the rule that other new dependencies still require a demonstrated need.

## Engineering Requirements

These requirements apply to every feature.

- Every feature task list MUST include acceptance tests derived from the specification's acceptance scenarios.
- Acceptance-test tasks MUST appear before the implementation tasks they verify.
- Implementation MUST follow test-driven development: write a test first, observe it fail for the expected reason, implement the minimum behavior needed to pass, and then refactor while keeping the tests green.
- The project's automated testing framework MUST be pytest.
- Tests MUST include unit, integration, and HTTP-level tests as appropriate to the behavior being verified.
- A feature task list without explicit automated test tasks is incomplete.
- Completion MUST require 100% branch coverage of project-owned executable application code. Line coverage is informational only.
- Coverage MUST exclude third-party dependencies, test code, and generated code. Any further exclusion MUST be explicitly justified and documented.

## Quality and Verification Requirements

- After implementation, every user-facing HTTP behavior MUST be verified against the running application using reproducible curl commands.
- The task list MUST contain explicit tasks for these curl-based acceptance checks.
- Verification MUST cover successful behavior and the applicable failure outcomes from the specification.
- Completion MUST require recorded evidence of test execution, branch coverage, and curl verification.
- A feature MUST NOT be claimed complete solely because implementation code exists or because automated tests pass.

## Limits

These are project-wide engineering and quality constraints, not feature-specific implementation details.

Do not modify feature specifications, plans, task lists, or application code.

Do not create a Git commit.
