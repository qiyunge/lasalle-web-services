# Research: Student Self-Enrollment

Date: 2026-10-16

Sources: the accepted specification, constitution 6.0.1, and the
current `lab-4/` service. Lab 3 was not read.

The constitution no longer names a required stack. An existing
technology decision should be reused unless a requirement or evidence
justifies a change. A new library still needs a demonstrated need.

## Language

**Requirement**: One local college service that already runs this
slice, with domain code free of third-party libraries.

**Existing**: `requires-python = ">=3.12"`. Domain modules use the
standard library only.

**Decision**: Keep Python 3.12.

**Rationale**: The service, tests, and SQLite access already run on
3.12. No requirement needs another language. Replacing it would rewrite
every module.

**Alternatives considered**: A newer Python, or another language.
Neither fixes a stated gap. The move would be cost without a
requirement.

**Trade-off**: The project stays on one language release. A later
upgrade is a separate decision.

## Web framework

**Requirement**: Translate an external request into an
application-owned input contract, invoke a driving port, and translate
the outcome. The framework must not enter the core.

**Existing**: Flask 3.1.3 is the only production dependency.
`college.adapters.inbound.http` and `college.app` are the only
production modules that import it. No Flask extension is installed.

**Decision**: Keep Flask 3.1.3 with no extensions.

**Rationale**: The adapter already maps JSON to the use case and maps
outcomes to status and body. Browse and enrollment do not need
background jobs, a schema generator, or a second routing style.

**Alternatives considered**:

- FastAPI. Comparable for a small JSON service, and it documents
  request bodies. Adopting it would replace the working adapter and
  add a dependency for behavior the current adapter already has.
- Django. Brings an ORM, admin, and project layout this slice does
  not use.
- No framework, standard-library HTTP only. Possible, and it would
  remove Flask. It would also replace request parsing and the test
  client already used by the HTTP tests.

**Trade-off**: Flask stays as the delivery mechanism. The core must
continue to receive an application input contract, not `request`.

## Persistence

**Requirement**: Store an inscription so a later duplicate is visible.
Overlapping enrollments for the same student and course leave exactly
one inscription. Domain code must not see rows or connections.

**Existing**: Standard-library `sqlite3`. Outbound adapters own the
connection and the row. Enrollment uses one `BEGIN IMMEDIATE`
transaction. `UNIQUE (student_id, course_id)` raises a conflict the
application maps to the already-enrolled sentence.

**Decision**: Keep SQLite through `sqlite3`. Do not add an ORM.

**Rationale**: The uniqueness conflict and the transaction boundary
already match the specification. `sqlite3` is not an extra dependency.
An ORM would put query objects closer to the core for no new query.

**Alternatives considered**: PostgreSQL, or SQLAlchemy. Both add
operations and a library. This slice is one local college service.
Nothing in the specification requires concurrent servers or a hosted
database.

**Trade-off**: SQLite is a single-file database. That fits the stated
scope. It is not a plan for a multi-server deployment.

## Test runner

**Requirement**: Automated tests for the specification and the domain
invariants, at unit, integration, and external-interface levels where
those levels can see the behavior. Branch coverage of new or modified
business code. The constitution does not name the runner.

**Existing**: pytest and pytest-cov are the dev extra. `addopts` fail
the run when branch coverage of `college` is under 100. Unit tests and
integration tests already exist. HTTP tests use Flask's test client.
`quickstart.md` also runs curl against the process.

**Decision**: Keep pytest and pytest-cov.

**Rationale**: The runner, the coverage gate, and the current tests
are one setup. Replacing the runner would rewrite that setup without
changing what is verified.

**Alternatives considered**: `unittest` from the standard library.
It avoids the pytest dependency. It would drop the current coverage
command and the existing test style. That cost is not justified by a
gap in what the tests observe.

**Trade-off**: pytest remains a development dependency. It is not a
runtime dependency and it is not imported by domain code.

## Static checks

**Requirement**: Principle Q3 runs the lint and type checks the
project has configured. It does not by itself add a tool. Principle E3
allows a new development dependency when a need is demonstrated.

**Existing**: `pyproject.toml` has no linter and no type checker. The
dev extra is pytest and pytest-cov. `enroll` still takes raw
identifiers. The plan adds validated commands and domain identity
types on the boundary between application, domain, and infrastructure.

**Decision**: Adopt Ruff and Pyright as development dependencies for
this feature. Configure Ruff with `E4`, `E7`, `E9`, and `F`. Configure
Pyright in basic mode. Limit both to `src/college`. Do not install
them until the plan is approved.

**Rationale**: Ruff is a lightweight lint for Python quality. Pyright
checks types. pytest checks runtime behavior, and branch coverage
measures which branches ran. Neither sees a primitive left on a
validated command. The new command and identity types make that static
check relevant. The minimal rule set and basic mode avoid a
project-wide strict rewrite.

**Alternatives considered**:

- Leave both tools out. Tests would still cover behavior. They would
  not check the typed boundary this feature is adding.
- Flake8 or Pylint instead of Ruff. They lint, and they would still be
  a new dependency, with a heavier default rule set.
- Mypy instead of Pyright. It can check types. Basic Pyright is the
  selected checker for the boundary, without a strict project-wide
  setting.
- Strict Pyright for the whole repository. That would force unrelated
  annotation work outside this feature.

**Trade-off**: Two development dependencies and a new gate for
`src/college`. The gate is small. A genuine error in that package is
fixed rather than suppressed. Tests and the 100% branch-coverage gate
stay.

## Application input contract

**Requirement**: The inbound adapter produces an application-owned
input contract that may hold unvalidated primitives. A validated
command uses domain types. Domain behavior does not see invalid
objects. Independent input-validation failures are returned together.
The accepted specification still shows one business message, the first
match in FR-014.

**Existing**: `enroll` takes raw identifiers and optional `note` and
`student_id`. The HTTP adapter rejects the first shape problem and
then calls `enroll`. Business refusals return on the first match.

**Decision**: Keep three responsibilities separate.

- Input validation is application coordination. The input contract may
  hold unvalidated primitives. Missing and non-integer required
  identifiers are independent input failures. The application collects
  them as typed errors with stable codes. It does not decide a grade
  attempt, an attempt to enroll someone else, registration, course
  existence, or a duplicate.
- Domain type construction belongs to domain types. After the required
  identifiers can be constructed, the validated command carries those
  domain types. The application does not copy the domain invariant.
- The input contract keeps `note`, and any named target student, as
  unvalidated facts for the use case. A target student is not an
  accepted enrollment field. The validated command carries only the
  acting student and course identifiers. Domain behavior does not
  receive those unvalidated facts.
- A programme is an identifier plus a nonempty name. Construction
  rejects a programme that lacks either. That rejection is the
  existing not-registered outcome when a student refers to it.
- Business authorization belongs to the use case. It reads the input
  contract for `note` and a named target student, and it reads the
  validated command for domain behavior. It keeps the accepted FR-014
  order and returns one business message.

RF-001 is resolved by constitution 6.0.1. Business refusals stay on
FR-014. UD-001 is resolved. More than one identifier failure is HTTP
400 with an `errors` array of stable codes and field names, as written
in the contract.

**Rationale**: Principle A10 assigns coordination to application code
and invariants to domain types. Principle A4 assigns protocol
translation to the adapter. FR-014 assigns the business message. Those
are different responsibilities. Merging them would either hide a
domain rule in the adapter or replace an accepted message rule.

**Alternatives considered**: Leave the fail-fast shape checks in the
HTTP adapter. That keeps the current code and leaves independent input
failures uncollected. Return every matching business sentence together.
That changes FR-014. Both are rejected.

**Trade-off**: One identifier failure still uses the existing
`message` sentence. More than one uses the `errors` array. Callers see
two response shapes for input validation. Business refusals stay one
`message`.

## Package names

**Requirement**: Keep explicit boundaries for domain, application, and
adapters.

**Existing**: `college.domain`, `college.application`, and
`college.adapters`.

**Decision**: Keep those package names. Do not rename them to a
literal `core/` tree.

**Rationale**: The three boundaries already exist. A rename would
change public imports and every test without changing a rule.

**Alternatives considered**: Move packages to `core/domain` and
`core/application`. Clearer as a diagram, costly as a move, and not
required for the boundary to be checkable.

**Trade-off**: A reader of the constitution has to map `college.domain`
to the domain boundary. The import graph already shows that boundary.
