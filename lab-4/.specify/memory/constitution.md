<!--
Sync Impact Report
- Version change: 6.0.0 → 6.0.1
- Bump: PATCH. A10 clarifies that accumulation applies to independent
  input-validation failures. A business refusal stays in the accepted
  feature specification and is not accumulated under A10.
- Modified principles:
  - A10. Core Boundary Validation → A10. Core Boundary Validation
- Added sections: none
- Removed sections: none
- Checked and unchanged: A4, A6, and A9 already keep unvalidated facts
  on the application input contract and require validated domain types
  for domain behavior.
- Follow-up TODOs: none
-->

# Lab-4 College Management Constitution

The college management service serves college staff and students.

This constitution governs architecture, engineering practices, quality
gates, and amendment decisions. Feature specifications own business
rules, feature-specific behavior, API contracts, and messages. Plans
and tasks own concrete designs and execution steps.

Rules are grouped: A for architecture, E for engineering, Q for
quality, and G for gap governance. A business rule belongs in the
accepted feature specification. This constitution does not adopt one.

## Core Principles

### A1. Full Bridge Hexagonal Architecture

The system MUST use Full Bridge Hexagonal Architecture. The core
consists of a distinct Application layer and a distinct Domain layer.
Infrastructure and delivery mechanisms remain outside the core.

The Application layer owns use cases, business orchestration,
application workflows, and the inbound and outbound ports. It MAY use
a third-party library when Principle E3 is met.

The Domain layer owns domain models, business behavior, and domain
invariants. It MUST remain independent of third-party libraries and
infrastructure frameworks.

An adapter MUST communicate with the core through an explicitly defined
port and a boundary mapping. An adapter MAY depend on core contracts
and on domain types. Dependencies MUST point inward: an adapter depends
on the core, and Application depends on Domain.

The composition root MAY depend on both the core and adapters for
dependency injection and application assembly. It MUST NOT contain a
business rule.

Rationale: Business behavior stays testable without a delivery
framework or a storage implementation. Delivery and storage translate
at the boundary. They are not the core.
Inward dependencies keep infrastructure outside the core. The
composition root only assembles the application.

### A2. Clean DDD Domain

Domain MUST model business behavior with the DDD building block that
owns the rule. The building blocks are an entity, a value object, an
aggregate and its aggregate root, a domain service, a domain event, a
domain factory, and a domain policy or specification.

A building block SHOULD be introduced only when an actual domain
requirement justifies it. The domain model that owns an invariant MUST
enforce that invariant. Domain behavior and a business rule MUST live
in that model. An application handler MUST NOT duplicate them.

When the domain uses an aggregate, that aggregate MUST define its
consistency boundary and MUST protect the invariants inside it.

Domain MAY use the language standard library. Domain MUST NOT depend
on Application, on an adapter, on a third-party package, on a
framework, or on persistence, transport, or other infrastructure.

Rationale: An invariant that lives only in an adapter, or is copied
into a handler, is not a domain rule. A Domain dependency on a delivery
framework, a database implementation, or Application would bind the
rule to its surroundings. A building block with no domain requirement
adds no consistency boundary.
SHOULD, rather than MUST, keeps an unused construct out of the model.

### A3. Application Use Cases

Application MUST define the driving ports that expose use cases.
Application MUST orchestrate the business operation by coordinating
domain behavior, outbound ports, and the transaction workflow.

Application MAY depend on Domain. Application MAY use a third-party
library when Principle E3 is met. Application MUST NOT depend on a
concrete adapter. Application MUST NOT import a concrete infrastructure
implementation or an infrastructure-specific representation.

Rationale: The use case decides the operation. A dependency on an
adapter, a repository class, or a database row would hide that decision
in infrastructure.

### A4. Inbound Boundary

An inbound adapter MUST translate an external request into an
application-owned input contract and MUST invoke a driving port.

An application-owned input contract MAY contain unvalidated primitive
values. A validated application command MUST use the appropriate domain
types.

An external transport object, a framework-specific request, and an
external DTO MUST NOT cross into the core. The inbound adapter MUST
translate an application outcome into the external protocol. It MUST
NOT duplicate a domain validation rule.

Rationale: Application owns the input contract and the coordination of
validation. The adapter owns protocol translation. Domain owns its
invariants.

### A5. Outbound Boundary

An application-owned outbound port MUST define the capability a use
case needs from persistence or from another external service. The
port's contract MUST use core-defined types.

An outbound adapter MUST implement that port. It MUST translate
infrastructure data into those core-defined types, and core-defined
types into its infrastructure representation, at the boundary.

The core MUST NOT use a database row, a database connection, a client
response, or an equivalent infrastructure-owned type.

Rationale: The use case asks for a capability. The adapter owns the
persistence query, the connection, and the infrastructure
representation.

### A6. Boundary Type Ownership

At each independent boundary between the core and the outside, the
contract and the data representation MUST be owned by the core. An
adapter MUST convert types explicitly where the outside uses a
different representation.

The required conversions are:

- Inbound: an external DTO becomes an application-owned input contract.
- Application to Domain: Application MUST supply validated domain
  types. A redundant data-transfer object is not required.
- Core to an outbound adapter: the core uses an explicit port and a
  boundary mapping.
- Outbound adapter to the core: infrastructure data becomes a
  core-defined type.

Internal core interactions MUST NOT introduce an unnecessary
data-transfer layer. Full Bridge does not require a one-to-one
data-transfer object inside the core.

Rationale: Translation belongs at the outside boundary. Copying the
same fields between two core types adds no architectural boundary.

### A7. Transactions and Integrity

A use case MUST preserve the business invariants adopted by the
accepted feature specification across persistence operations, including
conflicts and partial failures.

Application MAY coordinate a transaction through an abstract outbound
contract. An infrastructure adapter implements the transaction mechanics.
A business decision MUST NOT be hidden in an inbound adapter or an
outbound adapter.

Rationale: A conflict or a partial write is still a business outcome.
The adapter reports the persistence fact. The use case decides what that
fact means.

### A8. Capability Boundaries

Programme, student, course, and inscription responsibilities MUST remain
distinguishable. A cross-capability dependency MUST have a concrete
use-case justification and MUST satisfy Principles A1 through A7 and
A9 through A11.

Rationale: Each capability owns its rules. A dependency with no use-case
justification couples two capabilities for no business reason.

### A9. Domain Types and Value Objects

A domain-significant value MUST be an explicit domain type when domain
behavior uses it. It MUST NOT remain an unstructured primitive in a
validated application command or in domain behavior.

A value object MUST encapsulate its intrinsic invariants. A supported
interface MUST NOT create an invalid instance.

A primitive type MAY be used inside a value object, for a
domain-neutral implementation detail, in an application input contract
before validation, and at an external boundary before conversion into
a domain type.

A business rule MUST be assigned to the value object, entity,
aggregate, or domain service that owns it.

Rationale: A primitive string or number does not protect a domain
invariant. The type that owns the rule is the place that can reject an
invalid value. Primitives remain available where they carry no domain
meaning, and at the boundary that Principle A6 converts.

### A10. Core Boundary Validation

Application MUST coordinate validation and conversion of unvalidated
input before it invokes domain behavior that requires validated domain
types.

Domain MUST enforce its intrinsic invariants. Domain MUST NOT permit an
invalid domain object.

Independent input-validation failures MUST be accumulated and returned
together as a structured, non-empty collection of typed validation
errors with stable error codes. The core MUST NOT fail fast on the
first of those independent failures.

This accumulation applies to independent input-validation failures. A
business refusal is governed by the accepted feature specification. It
is not an input-validation failure, and it MUST NOT be accumulated
under this principle.

A validation that depends on another input MUST run only when that
prerequisite input is valid.

Application MUST coordinate that validation without duplicating a
domain rule. The inbound adapter translates the validation outcome into
the protocol-specific response under Principle A4.

Invalid input MUST NOT reach domain behavior that requires validated
values.

Rationale: Application coordinates validation. Domain owns the
invariants. The adapter owns protocol translation. A caller can correct
every independent input mistake from one response. An invalid domain
object is still not created. A business refusal keeps the priority the
feature specification states. This principle does not replace that
priority.

### A11. Package Organization

The project MUST keep an explicit architectural boundary between
`core/domain`, `core/application`, and `adapters`.

Package organization MUST balance development convenience, high
cohesion, low coupling, domain meaning, and a clear external API. A
package or module name MUST state its domain meaning, its
architectural responsibility, and its intended use.

A public import path MUST expose a stable domain or application
concept. It MUST NOT reveal an internal implementation detail that
callers do not need.

An internal structure MAY be reorganized when the public contract is
unchanged. A change to a public API MUST be deliberate, and its impact
MUST be evaluated.

During planning, an agent MAY choose the internal package structure.
That choice MUST preserve the architectural boundaries, semantic
correctness, and public API stability.

A new package or abstraction SHOULD be added only when it improves
cohesion, clarity, maintainability, or meaningful encapsulation. A
directory SHOULD be added when domain complexity requires it. Package
organization MUST follow architectural ownership and dependency
boundaries.

Rationale: The three boundaries are how Principles A1 through A6 stay
visible in the tree. A public path that exposes an internal module
makes the boundary unverifiable. An extra package, added before the
domain needs it, is structure with no rule to protect. SHOULD, rather
than MUST, allows a package when the improvement is real and delay
when it is not.

### E1. Research-Driven Technology Selection

Technology choices MUST be evaluated during the Research phase against
functional requirements, architectural constraints, engineering quality,
feasibility, maintainability, and operational complexity.

Existing technology decisions SHOULD be reused unless new requirements
or evidence justify reconsideration.

Research outcomes MUST inform the implementation plan. Technology
choices that preserve the principles in this constitution MUST NOT
require a constitutional amendment.

Rationale: Technology selection is a research and design responsibility,
not a constitutional constraint. This constitution governs the
principles a technology decision must satisfy. A concrete stack,
framework, or tool belongs in the plan or the feature specification.
SHOULD, rather than MUST, keeps an existing decision unless new
requirements or evidence justify a change.

### E2. Established Conventions

New code MUST follow the consistent conventions already present in the
project, unless a justified improvement is adopted. Naming and module
responsibilities MUST stay coherent with Principles A1 through A11.

Rationale: A second naming scheme, or a second home for the same
responsibility, makes the architecture harder to check.

### E3. Minimal Justified Complexity

A new library, pattern, abstraction, or infrastructure component MUST
have a demonstrated need. A feature-local design MAY evolve
incrementally. It MUST NOT waive Principles A1 through A11.

A new dependency MUST have its own demonstrated need.

Rationale: Additional complexity is justified only when it has a
demonstrated need. Incremental design does not remove Principles A1
through A11.

### E4. Explicit Errors

An expected business failure MUST be represented and handled explicitly.
An infrastructure failure MUST NOT be reported as business success.

Translation of an outcome into a protocol-specific status and response
belongs in the inbound adapter.

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
   Existing passing tests MUST stay passing. Principles A1 through A11
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

Automated tests MUST verify the accepted feature specification and the
applicable domain invariants.

Domain invariants and application use cases MUST be independently
testable. Tests MUST exercise the unit level, the integration level, and
the external-interface level wherever that level can observe the
behavior being verified. A level that cannot observe the behavior is
not required for that behavior.

The test framework and tools MUST be selected in Research. This
constitution MUST NOT mandate them.

Rationale: Each level is required only where it can see the behavior
under test. The runner is a technology choice under Principle E1, not
a standing constraint.

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

### Q5. Running Service Verification

After implementation, externally observable service behavior MUST be
verified against the running application. The verification MUST use
reproducible requests or an equivalent integration mechanism.

The verification MUST cover the applicable success and failure
outcomes. It MUST remain independent of in-process test clients.

The task list MUST include these checks.

Rationale: An in-process test client can pass while the running
service still disagrees with the specification.

### Q6. Completion Evidence

A feature MUST NOT be declared complete until all of the following hold:

- The accepted specification scenarios pass.
- The relevant automated tests pass.
- The configured static checks in Principle Q3 pass.
- Principle Q4 is satisfied.
- Principle Q5 passes where the feature has externally observable
  service behavior.
- Known critical defects are resolved.

The agent MUST give a concise completion report. The report MUST include
the test results, the branch-coverage results, the static-check results,
the applicable running-service verification results, and any unresolved
issues.

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
checks, or the running service behavior. The report is the completion
gate.
A permanent file is required only when a request asks for one.

### G1. Feature-Driven Review

A feature MUST be checked against the architecture constraints in this
constitution, and against the business rules in its accepted feature
specification, at specification, at design, and at implementation.

Before the next feature that materially depends on the same area, review
the missing rules, conflicts, duplication, overconstraints, and repeated
friction observed so far.

Rationale: A constraint checked only at the end is found after the
design has already ignored it. Repeated friction is the signal for
Principle G3.

### G2. No Silent Override

A feature MUST NOT silently override a constitutional constraint. A
discovered conflict MUST be surfaced for an explicit decision. A change
to a business rule belongs in the feature specification. A change to
cross-feature architecture requires architect review.

Rationale: An implementation that quietly breaks a rule makes this
constitution false. A business rule changes by amending the
specification that owns it. Architect review keeps shared structure
from changing as a side effect of one feature.

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

### G5. Accepted Specification Continuity

A feature MUST preserve the applicable business rules established by
previously accepted feature specifications.

A conflict between accepted feature specifications MUST be identified
and explicitly resolved before implementation.

Rationale: A later feature does not erase a rule an earlier accepted
specification established. An unresolved conflict would let
implementation choose one rule without a decision. Explicit resolution
keeps one adopted rule in force.

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
- **value object**: A domain type defined by its values that rejects an
  invalid instance.
- **aggregate / aggregate root**: A consistency boundary and the entity
  that protects the invariants inside it.
- **application input contract**: An application-owned input to a
  driving port. It may contain unvalidated primitive values. It MUST
  NOT contain an external transport type.
- **validated command**: An application-owned command expressed with
  validated domain types.
- **composition root**: The assembly point that wires adapters to core
  ports. It contains no business rule.

## Governance

Architecture constraints in this constitution govern feature
specifications and plans. A business rule belongs in the accepted
feature specification. A plan and a task list define implementation
and verification.

When a constraint conflicts with a feature need, that conflict MUST be
resolved under Principles G1, G2, and G5 before implementation behavior
changes.

This constitution governs architectural boundaries, engineering
practices, and quality gates. It does not adopt a business rule.
Enrollment, authority, identity, membership, and grade belong in the
accepted feature specification. It MUST NOT define a SQL schema, a
table, an index, a repository implementation, an API endpoint design,
or the shape of an identifier.

An amendment MUST be written into this file. It MUST name the affected
rules, the motivation, and the impact, and it MUST update the version
and the last-amended date in the same change.

Versioning follows semantic versioning:

- MAJOR: remove or redefine an adopted constraint.
- MINOR: add a constraint, a vocabulary entry, or a specification
  requirement.
- PATCH: clarify wording without changing a rule.

Compliance review:

- A feature specification MUST be checked against Principles Q1 and G5
  before it is accepted. Its business rules are part of that
  specification, not of this constitution.
- A design and an implementation MUST be checked against Principles A1
  through A11, E1 through E6, and G5 before they are accepted.
- A task list and a completion claim MUST be checked against Principles
  E5 and Q1 through Q6.

**Version**: 6.0.1 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-16
