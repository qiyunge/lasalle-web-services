<!--
Sync Impact Report
- Version change: 2.0.3 → 2.0.4
- Bump: PATCH. E5 already required Red and Green to be verified for a
  behavior change, and existing tests before and after a
  behavior-preserving change. Q6 already said Red and Green need no
  permanent per-cycle record. This amendment states both cases in E5
  and Q6, and applies the no-permanent-record rule to both.
- Modified principles:
  - E5. Test-Driven Development → E5. Test-Driven Development
  - Q6. Completion Evidence → Q6. Completion Evidence
- Added sections: none
- Removed sections: none
- Follow-up TODOs: none
-->

# Lab-4 College Management Constitution

The college management web service serves college staff and students.
Students may browse courses and enroll themselves. The service uses
Python 3.12, Flask, and SQLite.

This constitution governs project-wide business invariants, architecture,
engineering practices, quality gates, and amendment decisions. Feature
specifications own feature-specific behavior, API contracts, and
messages. Plans and tasks own concrete designs and execution steps.

Rules are grouped: B for business invariants, A for architecture, E for
engineering, Q for quality, and G for gap governance. Rules B1 through B7
are domain rules. They are not a SQL schema, an endpoint design, or a
repository method specification.

## Core Principles

### B1. Programme Membership

Every student MUST belong to an existing programme.

Rationale: A student is a learner registered in a programme. A record
that names a missing programme is not a valid registration.

### B2. Student Identity

A student MUST have an identifier, a nonempty name, and a nonempty email
address. Student email addresses MUST be unique.

Rationale: A student without a name or an email address is not a complete
registration. Two students MUST NOT share an email address.

### B3. Course Identity

A course MUST have an identifier, a nonempty code, and a nonempty name.
Course codes MUST be unique. Course names MAY repeat.

Rationale: The code distinguishes one course from another. The name is
required so the course can be recognized. Two courses MAY share a name
when their codes differ.

### B4. Enrollment Integrity

Every inscription MUST reference an existing student and an existing
course. A student MUST NOT have more than one inscription for the same
course.

Rationale: An inscription is the record of one student's enrollment in
one course. A second inscription for the same pair is a conflict. A
reference to a missing student or course is not an enrollment.

### B5. Grade

An inscription MAY have no note. An assigned note MUST satisfy the range
stated by the accepted feature specification. This constitution does not
invent a numerical range.

Rationale: A note is the optional grade on an inscription. The permitted
range is a feature decision. A value outside the range that feature
states is not a valid note.

### B6. Explicit Failure

A missing reference, a duplicate enrollment, or a violated invariant MUST
produce an explicit failure. It MUST NOT succeed silently. The feature
specification defines the applicable user-facing messages.

Rationale: Staff and students MUST be able to tell that the operation
did not take effect. Silent success would hide a broken invariant.

### B7. Student Authority

A student MAY browse courses and MAY enroll without staff intervention.
A student MUST NOT enroll on another student's behalf. A student MUST NOT
assign, change, or remove any grade. Grade management is reserved for
authorized staff. Student withdrawal is not authorized until a feature
specification adopts it.

Rationale: Student authority is browsing and self-enrollment. Another
student's inscription, a grade, and withdrawal are outside that
authority.

### A1. Full Bridge Hexagonal Architecture

The system MUST use Full Bridge Hexagonal Architecture. The domain core
consists of a distinct Application layer and a distinct Domain layer.
Infrastructure and delivery mechanisms remain outside the core.

Rationale: Business behavior stays testable without Flask or SQLite.
Delivery and storage translate at the boundary. They are not the core.

### A2. Clean DDD Domain

Domain MUST model business behavior with the appropriate DDD building
block: an entity, a value object, or a domain service. The domain model
that owns an invariant MUST enforce that invariant.

Domain MAY use the Python standard library. Domain MUST NOT depend on
Application, on a third-party package, on a framework, or on persistence,
transport, or other infrastructure.

Rationale: An invariant that lives only in an adapter is not a domain
rule. A Domain import of Flask, SQLite, or Application would bind the
rule to its surroundings.

### A3. Application Use Cases

Application MUST define the driving ports that expose use cases.
Application MUST orchestrate the business operation by coordinating
domain behavior, outbound ports, and the transaction workflow.

Application MAY depend on Domain. Application MAY use a third-party
library when Principle E3 is met. Application MUST NOT import a concrete
infrastructure implementation or an infrastructure-specific
representation.

Rationale: The use case decides the operation. An import of a repository
class or a database row would hide that decision in infrastructure.

### A4. Inbound Boundary

An inbound adapter MUST translate an external request into an
application-owned input contract and MUST invoke a driving port.

An external transport type, including a Flask request, MUST NOT cross
into the core. The inbound adapter MUST translate the application
outcome into the external protocol.

Rationale: The core stays free of HTTP. The adapter owns status codes
and response bodies. The use case owns the business outcome.

### A5. Outbound Boundary

An application-owned outbound port MUST define the capability a use case
needs from persistence or from another external service. An outbound
adapter MUST implement that port and MUST translate between its
infrastructure representation and the port's contract.

The core MUST NOT use a SQLite row, a database connection, an HTTP client
response, or an equivalent infrastructure-owned type.

Rationale: The use case asks for a capability. The adapter owns the SQL,
the connection, and the row shape.

### A6. Boundary Type Ownership

At each independent boundary between the core and the outside, the
contract and the data representation MUST be owned by the core. An
adapter MUST translate where the outside uses a different representation.

Application and Domain MAY share domain types. A separate data-transfer
object is not required merely because an internal function or port is
called. Full Bridge does not require a redundant one-to-one
data-transfer object inside the core.

Rationale: Translation belongs at the outside boundary. Copying the same
fields between two core types adds no architectural boundary.

### A7. Transactions and Integrity

A use case MUST preserve business invariants across persistence
operations, including conflicts and partial failures.

Application MAY coordinate a transaction through an abstract outbound
contract. An infrastructure adapter implements the transaction mechanics.
A business decision MUST NOT be hidden in a Flask adapter or a SQLite
adapter.

Rationale: A conflict or a partial write is still a business outcome.
The adapter reports the persistence fact. The use case decides what that
fact means.

### A8. Capability Boundaries

Programme, student, course, and inscription responsibilities MUST remain
distinguishable. A cross-capability dependency MUST have a concrete
use-case justification and MUST satisfy Principles A1 through A7.

Rationale: Each capability owns its rules. A dependency with no use-case
justification couples two capabilities for no business reason.

### E1. Technology Baseline

The service MUST use Python 3.12, Flask, and SQLite until a
constitutional amendment changes that stack.

Rationale: These are the adopted language, web framework, and database.
Replacing any of them is an infrastructure change, not a feature
decision.

### E2. Established Conventions

New code MUST follow the consistent conventions already present in the
project, unless a justified improvement is adopted. Naming and module
responsibilities MUST stay coherent with Principles A1 through A8.

Rationale: A second naming scheme, or a second home for the same
responsibility, makes the architecture harder to check.

### E3. Minimal Justified Complexity

A new library, pattern, abstraction, or infrastructure component MUST
have a demonstrated need. A feature-local design MAY evolve
incrementally. It MUST NOT waive Principles A1 through A8.

pytest, required by Principle Q2, is a demonstrated need. Any other new
dependency still requires its own demonstrated need.

Rationale: An extra abstraction is justified only when the adopted shape
cannot meet the need. Incremental design does not remove a mandatory
boundary.

### E4. Explicit Errors

An expected business failure MUST be represented and handled explicitly.
An infrastructure failure MUST NOT be reported as business success.

Translation of an outcome into an HTTP status and message belongs in the
inbound adapter.

Rationale: A caller MUST be able to tell a refused operation from a
completed one. The adapter owns the protocol and does not invent the
business result.

### E5. Test-Driven Development

For new or changed observable behavior, the Red, Green, Refactor cycle
is mandatory.

1. Red. Write automated tests from the feature specification and its
   acceptance criteria before implementing that behavior. Run the tests
   and verify that they fail for the expected behavioral reason.
2. Green. Implement the minimum change that makes those tests pass.
   Existing passing tests MUST stay passing. Principles A1 through A8
   MUST stay satisfied.
3. Refactor. Improve structure without changing observable behavior.
   Every affected test MUST still pass.

For behavior-preserving refactoring and non-behavioral maintenance,
existing relevant tests MUST pass before the change and after it. A new
failing test is not required unless the work exposes previously
unspecified or untested behavior.

A test MUST NOT be weakened, deleted, bypassed, or rewritten only to fit
an incorrect implementation.

A task list MUST schedule specification-derived acceptance tests before
the implementation they verify. Tests that already pass do not
demonstrate the Red phase for newly specified behavior.

For new or changed observable behavior, Red and Green results MUST be
verified during execution. For behavior-preserving changes, the relevant
tests MUST pass before the change and after it.

Neither case requires a permanent log per cycle, a separate evidence
document, or a commit per cycle. Completion evidence is Principle Q6.

Rationale: A test written after a behavior change can pass without
showing that it detects the missing behavior. The Red result is that
evidence. A change that preserves behavior has no missing behavior for a
new test to detect, so the existing tests before and after the change
are the check. Newly exposed behavior is a behavior change and returns
to Red, Green, Refactor.

### E6. Decision Scope

A reversible implementation decision that stays inside one feature MAY
be made in that feature when it complies with this constitution. A
change to a cross-feature contract, or to a constraint in this
constitution, requires explicit review.

Rationale: A local, reversible choice does not need an amendment. A
choice that binds another feature, or that changes a rule in this file,
does.

### Q1. Specification and Acceptance

Every feature specification MUST identify its audience, the expected
behavior, the relevant failures including user-facing messages, the
explicit exclusions, and verifiable acceptance scenarios.

Rationale: Those items are what a later test and a later review can
check. A specification that omits one of them does not comply.

### Q2. Automated Verification

pytest MUST be the automated test runner.

Domain invariants and application use cases MUST be independently
testable. Tests MUST exercise the unit level, the integration level, and
the HTTP level wherever that level can observe the behavior being
verified. A level that cannot observe the behavior is not required for
that behavior.

Rationale: pytest is the adopted runner. Each level is required only
where it can see the behavior under test.

### Q3. Static Checks

Changed project-owned code MUST pass the lint and type checks the
project has already configured. An exception MUST be justified and
documented.

This principle does not add a linter, a type checker, or a setting. When
none is configured, there is no configured check to run.

Rationale: Skipping a check the project already configured hides a
defect that check was chosen to catch. Adding a tool is a dependency
decision under Principle E3, not a side effect of this rule.

### Q4. Branch Coverage

New or modified project-owned executable business code MUST achieve 100%
branch coverage of its applicable branches.

Coverage of new or modified business branches MUST be verified using
branch-level coverage data or an equivalent reproducible analysis. A
file-level coverage percentage alone MUST NOT be treated as proof of
incremental branch coverage.

Overall branch coverage of project-owned executable application code
MUST NOT fall below the established baseline, measured using the same
coverage scope and configuration.

The baseline MUST be established from a verified coverage report and
updated only through an explicit, justified decision.

Branch coverage MUST be measured with the project's configured coverage
tooling. Line coverage is informational and MUST NOT stand in for branch
coverage.

Third-party code, generated code, and test code are excluded. Any
further exclusion MUST be narrow, justified, and documented. An
exclusion MUST NOT conceal untested business behavior.

Coverage is necessary. It is not sufficient to show correctness.

Rationale: A new or changed business branch that never executed is an
untested decision. A file can report full coverage while a new branch
inside it was not executed, so the file percentage does not prove the
incremental rule. The baseline is a measured result, so a later run is
comparable only under the same scope and configuration. Changing that
measured gate requires an explicit decision that states why.

### Q5. Running HTTP Verification

After implementation, every user-facing HTTP behavior MUST be verified
against the running application with reproducible curl commands. The
commands MUST cover the applicable success and failure outcomes. The
task list MUST include these checks.

This verification is separate from tests that use Flask's test client.

Rationale: A test client can pass while the running service still
disagrees with the specification.

### Q6. Completion Evidence

A feature MUST NOT be declared complete until all of the following hold:

- The accepted specification scenarios pass.
- The relevant automated tests pass.
- The configured static checks in Principle Q3 pass.
- Principle Q4 is satisfied.
- Principle Q5 passes where the feature has user-facing HTTP behavior.
- Known critical defects are resolved.

The agent MUST give a concise completion report. The report MUST include
the test results, the branch-coverage results, the static-check results,
the applicable HTTP verification results, and any unresolved issues.

For new or changed observable behavior, Red and Green results MUST be
verified during execution. For behavior-preserving changes, the relevant
tests MUST pass before the change and after it, as Principle E5
requires.

Neither case requires a permanent log per cycle, a separate evidence
document, or a commit per cycle.

The completion report MAY be the agent's final task response. No further
permanent artifact is required unless a request asks for one.

A feature MUST NOT be declared complete only because implementation code
exists, or only because automated tests pass.

Rationale: Code or a green test run does not show coverage, static
checks, or the running HTTP behavior. The report is the completion gate.
A permanent file is required only when a request asks for one.

### G1. Feature-Driven Review

A feature MUST be checked against the current business and architecture
constraints at specification, at design, and at implementation.

Before the next feature that materially depends on the same area, review
the missing rules, conflicts, duplication, overconstraints, and repeated
friction observed so far.

Rationale: A constraint checked only at the end is found after the
design has already ignored it. Repeated friction is the signal for
Principle G3.

### G2. No Silent Override

A feature MUST NOT silently override a constitutional constraint. A
discovered conflict MUST be surfaced for an explicit decision. A change
to a business rule, or to cross-feature architecture, requires architect
review.

Rationale: An implementation that quietly breaks a rule makes this
constitution false. Architect review keeps business rules and shared
structure from changing as a side effect of one feature.

### G3. Evidence-Based Promotion

A finding SHOULD become a constitutional rule only when it is stable,
project-wide, and supported by implementation evidence or by an explicit
business decision. A feature-local detail stays in the specification,
the plan, the tests, or the code.

Rationale: One feature's choice is not yet a project rule. SHOULD, rather
than MUST, allows an explicit business decision to adopt a rule before
long evidence exists. The same rule permits that decision.

### G4. Lightweight Amendment

A ratified amendment MUST name the affected rules, the motivation, and
the impact. It MUST update the version and the last-amended date.

A routine prompt, a transient discussion, or a single iteration does not
require its own permanent record or its own commit. Version control
retains the history.

Rationale: An amendment that does not name the rule and the impact
cannot be reviewed. Ordinary iteration is already history in version
control.

## Domain Vocabulary

- **programme**: An academic programme offered by the college.
- **student**: A learner registered in a programme.
- **course**: A course offered by the college.
- **inscription / enrollment**: The record of one student's enrollment
  in one course.
- **note / grade**: The optional grade associated with an inscription.
- **driving port**: An application-owned interface that exposes a use
  case to an inbound adapter.
- **outbound port**: An application-owned interface for a capability
  supplied by an outbound adapter.

## Governance

Accepted business invariants and architecture constraints govern feature
specifications and plans. A feature specification defines behavior inside
those constraints. A plan and a task list define implementation and
verification.

When a constraint conflicts with a feature need, that conflict MUST be
resolved under Principles G1 and G2 before implementation behavior
changes.

This constitution supersedes informal descriptions of programmes,
students, courses, inscriptions, notes, and of how the service is
structured. It MUST NOT define a SQL schema, a table, an index, a
repository implementation, or an API endpoint design.

An amendment MUST be written into this file. It MUST name the affected
rules, the motivation, and the impact, and it MUST update the version
and the last-amended date in the same change.

Versioning follows semantic versioning:

- MAJOR: remove or redefine an adopted constraint.
- MINOR: add a constraint, a vocabulary entry, or a specification
  requirement.
- PATCH: clarify wording without changing a rule.

Compliance review:

- A feature specification MUST be checked against Principles B1 through
  B7 and Q1 before it is accepted.
- A design and an implementation MUST be checked against Principles A1
  through A8 and E1 through E6 before they are accepted.
- A task list and a completion claim MUST be checked against Principles
  E5 and Q1 through Q6.

**Version**: 2.0.4 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-15
