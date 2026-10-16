# Lab-4 College Management Constitution

**Status:** Candidate — not ratified  
**Proposed version:** 2.0.0  
**Baseline:** 1.4.0 (2026-10-14)  
**Proposed:** 2026-10-15

## Purpose and Scope

This constitution governs project-wide business invariants, architecture, engineering practices, quality gates, and amendment decisions for the College Management web service. Feature specifications own feature-specific behavior, API contracts and messages; plans and tasks own concrete designs and execution steps. The service serves college staff and students and uses Python 3.12, Flask, and SQLite.

## I. Business Invariants

**B1 — Programme membership.** Every student MUST belong to an existing programme.

**B2 — Student identity.** A student MUST have an identifier, a nonempty name, and a nonempty email address. Student email addresses MUST be unique.

**B3 — Course identity.** A course MUST have an identifier, a nonempty code, and a nonempty name. Course codes MUST be unique; course names MAY repeat.

**B4 — Enrollment integrity.** Every inscription MUST reference an existing student and course. A student MUST NOT have more than one inscription for the same course.

**B5 — Grade.** An inscription MAY have no note. Assigned notes MUST satisfy the range specified in the accepted feature specification; this constitution does not invent a numerical range.

**B6 — Explicit failure.** Missing references, duplicate enrollment, and violated invariants MUST produce explicit failure, not silent success. Feature specifications define applicable user-facing messages.

**B7 — Student authority.** Students MAY browse courses and enroll themselves without staff intervention. Students MUST NOT enroll on another student's behalf or assign, change, or remove any grade. Grade management is reserved for authorized staff. Student withdrawal is not authorized until separately specified.

These are domain rules, not SQL schemas, endpoint designs, or repository method specifications.

## II. Architecture Constraints

**A1 — Full Bridge Hexagonal Architecture.** The system MUST use Full Bridge Hexagonal Architecture. The domain core consists of distinct Application and Domain layers. Infrastructure and delivery mechanisms remain outside the core.

**A2 — Clean DDD Domain.** Domain MUST model business behavior using appropriate DDD entities, value objects, and domain services; invariants MUST be enforced by the responsible domain model. Domain MAY use the Python standard library but MUST NOT depend on Application, third-party packages, frameworks, persistence, transport, or infrastructure.

**A3 — Application use cases.** Application MUST define driving ports/use cases and perform business orchestration, coordinating domain behavior, outbound ports, and transaction workflows. Application MAY depend on Domain and use third-party libraries, but MUST NOT import or depend on concrete infrastructure implementations or infrastructure-specific representations.

**A4 — Inbound boundary.** Inbound adapters MUST translate external requests into application-owned input contracts and invoke driving ports. External transport types (for example, Flask Request) MUST NOT cross into the core. Responses MUST be translated into the external protocol by the inbound adapter.

**A5 — Outbound boundary.** Application-owned outbound ports MUST define the capabilities needed from persistence or other external services. Outbound adapters MUST implement those ports and translate between their infrastructure-specific representations and the port's contracts. The core MUST NOT use SQLite rows, database connections, HTTP client responses, or equivalent infrastructure-owned types.

**A6 — Boundary type ownership.** At each independent core/external boundary, contracts and data representations MUST be owned by the core and translated by adapters as necessary. Application and Domain MAY share domain types internally; no separate DTO is required merely because an internal function or port is called. Full Bridge does not mandate redundant one-to-one DTOs inside the core.

**A7 — Transactions and integrity.** Use cases MUST preserve business invariants across persistence operations, including conflicts and partial failures. Application MAY coordinate transactions through abstract outbound contracts; infrastructure adapters implement transaction mechanics. Business decisions MUST NOT be hidden in Flask or SQLite adapters.

**A8 — Capability boundaries.** Programme, student, course, and inscription responsibilities MUST remain distinguishable. Cross-capability dependencies MUST have a concrete use-case justification and MUST respect A1–A7.

## III. Engineering Constraints

**E1 — Technology baseline.** Python 3.12, Flask, and SQLite MUST be used until a constitutional amendment changes the stack.

**E2 — Established conventions.** New code MUST follow existing consistent project conventions unless a justified improvement is adopted. Naming and module responsibilities MUST remain coherent with the architecture.

**E3 — Minimal justified complexity.** New libraries, patterns, abstractions, and infrastructure components MUST have a demonstrated need. Feature-local design MAY evolve incrementally, but MUST NOT waive mandatory architectural boundaries.

**E4 — Explicit errors.** Expected business failures MUST be represented and handled explicitly. Infrastructure failures MUST NOT be silently reported as business success. Translation to HTTP status and message belongs in the inbound adapter.

**E5 — Test-driven development.** For each new or changed observable behavior, developers and AI coding agents MUST follow the Red → Green → Refactor cycle:

1. **Red:** Write automated tests derived from the feature specification and acceptance criteria before implementing the corresponding behavior. Execute the tests and verify that they fail for the expected behavioral reason.
2. **Green:** Implement the minimum change necessary to pass the failing tests while preserving existing passing tests and architectural constraints.
3. **Refactor:** Improve implementation structure without changing observable behavior. All affected tests MUST remain passing.

Tests MUST NOT be weakened, deleted, bypassed, or modified merely to accommodate an incorrect implementation.

Tasks MUST schedule specification-derived acceptance tests before the implementation they verify. Existing passing tests alone do not demonstrate the Red phase for newly specified behavior.

The Agent MUST verify actual Red and Green test execution results. Per-cycle logs and commits are NOT required; completion evidence is governed by Q6.

**E6 — Decision scope.** Reversible implementation decisions confined to a feature MAY be made locally when consistent with this constitution. Changes to cross-feature contracts or constitutional constraints require explicit review.

## IV. Quality Constraints

**Q1 — Specification and acceptance.** Every feature specification MUST identify its audience, expected behavior, relevant failures (including user-facing messages), explicit exclusions, and verifiable acceptance scenarios.

**Q2 — Automated verification.** pytest MUST be the automated test runner. Domain invariants and application use cases MUST be independently testable. Tests MUST exercise the unit, integration, and HTTP levels wherever those levels can observe the behavior being verified; a level unable to observe that behavior is not required for that behavior.

**Q3 — Static checks.** Changed project-owned code MUST pass the project's configured linting and type-checking checks. Exceptions MUST be justified and documented; tools or settings are not newly mandated here beyond those already configured.

**Q4 — Branch coverage.** New or modified project-owned executable business code MUST achieve **100% branch coverage** for all applicable branches.

Overall project branch coverage MUST NOT fall below the established baseline.

Branch coverage MUST be measured using the project's configured coverage tooling. Line coverage is informational and MUST NOT substitute for branch coverage.

Third-party, generated, and test code are excluded. Additional exclusions MUST be narrowly scoped, justified, and documented. Exclusions MUST NOT be used to conceal untested business behavior.

Coverage is necessary but not sufficient to demonstrate correctness.

**Q5 — Running HTTP verification.** After implementation, every user-facing HTTP behavior MUST be verified against the running application with reproducible `curl` commands covering the applicable success and failure outcomes. Tasks MUST include these checks. This is separate from Flask test-client verification.

**Q6 — Completion evidence.** A feature MUST NOT be declared complete until:

- Accepted specification scenarios pass.
- Relevant automated tests pass.
- Configured static checks pass.
- Q4's branch coverage requirements are satisfied.
- Q5's running HTTP checks pass where applicable.
- Known critical defects are resolved.

The Agent MUST provide a concise completion report containing test results, branch coverage results, static check results, applicable HTTP verification results, and any unresolved issues.

Evidence of the Red and Green phases MUST be verified during execution but does NOT require permanent per-cycle logs, separate documentation, or individual commits.

A completion report MAY be included in the Agent's final task response. No additional permanent artifact is required unless explicitly requested.

## V. Gap Governance

**G1 — Feature-driven review.** Features MUST be checked against current business and architecture constraints at specification, design, and implementation. Before the next materially related feature, review observed missing rules, conflicts, duplication, overconstraints, and repeated friction.

**G2 — No silent override.** A feature MUST NOT silently override a constitutional constraint. A discovered conflict MUST be surfaced for an explicit decision; business-rule and cross-feature architecture changes require architect review.

**G3 — Evidence-based promotion.** A finding SHOULD become a constitutional rule only if it is stable, project-wide, and supported by implementation evidence or an explicit business decision. Feature-local details remain in specifications, plans, tests, or code.

**G4 — Lightweight amendment.** Ratified amendments MUST identify affected rules, motivation, and impact, and update version and last-amended date. Routine prompts, transient discussions, and each individual iteration do not require permanent records or a separate commit. Normal version control retains code history.

## Domain Vocabulary

- **programme:** Academic programme offered by the college.
- **student:** Learner registered in a programme.
- **course:** Course offered by the college.
- **inscription / enrollment:** Record of one student's enrollment in one course.
- **note / grade:** Optional grade associated with an inscription.
- **driving port:** Application-owned interface exposing a use case to an inbound adapter.
- **outbound port:** Application-owned interface for a capability supplied by an outbound adapter.

## Governance and Precedence

Accepted business invariants and architecture constraints govern feature specifications and plans. Feature specifications define behavior within these constraints; plans and tasks define implementation and verification. If a constraint conflicts with feature needs, resolve the gap explicitly before changing implementation behavior.

Versioning uses semantic versioning: MAJOR for removing/redefining an adopted constraint; MINOR for adding one; PATCH for wording-only clarification. This proposed **2.0.0** is not ratified and does not replace v1.4.0 until approved.

**Version:** 2.0.0-candidate | **Ratified:** No | **Last Proposed:** 2026-10-15
