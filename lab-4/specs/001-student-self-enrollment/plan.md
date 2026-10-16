# Implementation Plan: Student Self-Enrollment

**Branch**: `001-student-self-enrollment` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-student-self-enrollment/spec.md`

## Summary

A registered student browses every existing course and enrolls in one
course without an administrator. The inscription belongs to that
student, names that course, has no grade, and stays observable. The
accepted refusal sentences and the FR-014 first-match order stay as
specified.

The service already implements that behavior with Python 3.12, Flask
3.1.3, and SQLite. Research keeps that stack. The design work is to
bring the inbound boundary in line with constitution 6.0.1 and the
updated specification. The acting student comes from a trusted caller
context. The enrollment request does not accept a target student. A
programme has an identifier and a nonempty name. Application code
validates required identifiers and builds a command of domain types.
Domain behavior sees only that command. More than one identifier
failure is HTTP 400 with an `errors` array. Business refusals stay on
FR-014.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Flask 3.1.3. No Flask extensions and no ORM.

**Storage**: SQLite through the standard-library `sqlite3` module. One
write transaction for enrollment. `UNIQUE (student_id, course_id)`
remains the overlap guarantee.

**Testing**: pytest and pytest-cov, already configured to require 100%
branch coverage of `college`. HTTP behavior is also checked with curl
against the running process. Ruff and Pyright are adopted as
development dependencies. They are not installed until this plan is
approved.

**Target Platform**: Local Python 3.12 web service.

**Project Type**: web-service

**Performance Goals**: No throughput target. A successful enrollment
is persisted and can be observed by the already-enrolled refusal on
the next attempt.

**Constraints**: Constitution 6.0.1. Accepted specification, including
FR-014. Domain stays free of third-party libraries. Rejected
operations do not write.

**Scale/Scope**: This slice browses courses and creates one
self-enrollment. Programmes, students, and courses already exist.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution 6.0.1. The specification owns the business rules. This
check separates four facts. Design compliance is the written design.
Planned implementation is work this plan describes and does not do.
Verified evidence is the current `lab-4` code and the recorded files
under `evidence/`. This planning pass did not re-run pytest or curl.
An unresolved conflict is not a waiver and is not a choice.

| Principle | Design compliance | Planned implementation | Verified evidence | Unresolved |
| --- | --- | --- | --- | --- |
| A1–A3, A8, A11. Core split, capability boundaries, package boundaries. | Complies. Keep `college.domain`, `college.application`, and `college.adapters`. `college.app` stays the composition root and holds no business rule. | No package move. | Domain and application modules do not import Flask, `sqlite3`, or adapters. Adapters import the core. `college.app` wires them. No automated boundary test exists. | None. |
| A4. Inbound adapter translates protocol and does not duplicate a domain rule. | Complies. The adapter builds an application input contract and maps one validation failure to the existing sentence, or more than one to HTTP 400 `errors`. | Move identifier checks out of `adapters/inbound/http.py`. | The adapter still reads the Flask request and returns the first shape sentence itself. | None. RF-001 and UD-001 are resolved. |
| A5–A7, E4. Outbound ports, core-owned types, transactions, explicit failure. | Complies. Ports stay application-owned. One write transaction. A uniqueness conflict is the already-enrolled outcome. An integrity failure is not success. | Keep the current ports and unit of work. | SQLite adapters translate rows. `enroll` rolls back on an invalid stored inscription and maps `PersistenceConflict` to the already-enrolled sentence. | None. |
| A2, A6, A9. Domain types. No redundant core DTO. | Complies for the target command. Identifier value objects are justified because a validated command must not carry raw identifiers. A programme name is a domain value. No new aggregate. | Add identifier value objects and a validated command that uses them. `Programme` must reject a missing name. | `Student`, `Course`, and `Inscription` reject invalid construction. `Programme` currently requires only an integer identifier. `enroll` still receives raw identifiers. | None. |
| A10. Application coordinates input validation. Independent input failures accumulate. Business refusals stay in the specification. | Complies. Identifier failures accumulate. FR-014 stays one business message. | Application collects independent identifier failures. The use case applies FR-014 from the input contract and passes only the validated command to domain behavior. | The adapter fail-fasts on the first shape error. The use case fail-fasts on the first FR-014 match. The multiple-error HTTP body is not implemented. | None. |
| E1, E2, E3, E6. Research, conventions, justified complexity, decision scope. | Complies. [research.md](research.md) keeps Python 3.12, Flask 3.1.3, `sqlite3`, pytest, and pytest-cov. Ruff and Pyright are added because validated commands and domain identity types need a static boundary check. The rule set stays minimal. | Add the two development dependencies and the configuration below. Do not install them before this plan is approved. | `pyproject.toml` still has only pytest and pytest-cov in the dev extra. | None. |
| E5, Q2, Q4. TDD and branch coverage. | The verification plan complies. | Behavior changes follow Red, Green, Refactor. New or modified business branches stay at 100% under the existing pytest-cov scope. | `evidence/coverage.txt` records 46 passing tests and 100% branch coverage of the current `college` package. That file is evidence of the current service, not of the planned boundary move. | None. |
| Q3. Configured static checks. | Complies once the configuration below is present. Q3 then requires those checks to pass. It does not require strict typing outside `src/college`. | Add Ruff and Pyright, then run the commands in Verification. | No linter or type checker is configured yet. | None. The packages are not installed until this plan is approved. |
| Q5, Q6. Running service and completion evidence. | The verification plan complies. Curl stays independent of the Flask test client. | Re-run curl after any later code change. Completion needs tests, branch coverage, and curl. | `evidence/curl.txt` records single-outcome requests against a running process. It does not record two invalid identifiers in one request, or two business rules in one request. | None. |
| G5. Accepted specification continuity. | Complies. FR-001 through FR-014 stay. No other feature specification exists. | No business-message change. | The specification states FR-014. RF-001 is resolved there without changing that rule. | None. |

Post-design: the same rows hold. Design compliance is not verified
evidence. The current service still fail-fasts on the first identifier
error. RF-001 and UD-001 are resolved in the design and are not yet
implemented.

## Project Structure

### Documentation (this feature)

```text
specs/001-student-self-enrollment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md             # not created by this plan
```

### Source Code (repository root)

```text
src/college/
├── app.py                          # composition root
├── domain/
├── application/
└── adapters/
    ├── inbound/
    └── outbound/

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep the current three-way split. The
composition root is `college.app`. It may depend on the core and the
adapters. Domain and application must not import adapters.

## What is constrained

1. **Constitution.** Boundaries, validation ownership, domain types,
   transactions, tests, coverage, and running-service checks.
2. **Accepted specification.** Browse and enrollment outcomes, the
   sentences, FR-014's single message, and the out-of-scope list.
3. **Existing technology.** Python 3.12, Flask 3.1.3, `sqlite3`,
   pytest, and pytest-cov are already in the project. Research keeps
   them. Ruff and Pyright are proposed development dependencies and
   are not installed yet.
4. **Recommended decisions.** Those are in [research.md](research.md)
   and in the design below.
5. **Resolved.** RF-001: business refusals stay on FR-014. UD-001:
   more than one identifier failure is HTTP 400 with an `errors`
   array of stable codes and field names.
6. **Entity attributes.** Programme, Student, and Course have an
   identifier and a nonempty name, as the accepted specification
   states. A programme name is not required to be unique. Inscription
   has an identifier and no name. See [data-model.md](data-model.md).
7. **Acting student.** A trusted caller context supplies the acting
   student. The request does not accept a target student. A successful
   inscription belongs to the acting student. Naming another student
   remains the existing self-only refusal. Authentication stays out of
   scope.

## Design

Three responsibilities stay separate. Input validation does not decide
authorization. Domain construction does not choose the student-facing
sentence. Authorization does not restate a domain invariant.

### Input validation

The HTTP adapter reads JSON and builds an application input contract.
The trusted caller context supplies `acting_student_id`. The contract
also carries `course_id`, the optional `note`, and any target student
the caller named. A target student is not an accepted enrollment
field. The Flask request does not enter the core. The adapter does
not decide the grade sentence, the self-only sentence, or the
identifier rules.

The application coordinates validation of the two required
identifiers. A missing identifier and an identifier that cannot form
a domain identifier are independent input failures. The application
collects every such failure into one typed result with stable codes.
It asks the domain type to accept or reject the value. It does not
copy that rule.

One failure still maps to the sentence the service already returns.
More than one is HTTP 400. The body is an `errors` array. Each element
has `code` and `field`. The codes are `acting_student_id_missing`,
`course_id_missing`, `acting_student_id_not_integer`, and
`course_id_not_integer`. The contract states the order and the example.
UD-001 is resolved by that body.

Optional `note`, and a named target student, stay unvalidated facts
on the input contract. The use case reads them for authorization.
They are not input-validation failures, and they are not placed on
the validated command.

### Domain type construction

A validated command exists only when both required identifiers are
domain types. The command contains the acting student identifier and
the course identifier. It does not contain a target student or
`note`.

`Student`, `Course`, and `Inscription` keep fail-closed construction.
`Programme` gains a nonempty name and rejects a programme that lacks
an identifier or that name. An invalid instance is not returned. A
stored programme that cannot be constructed is not an existing
programme, so the acting student is not registered. A stored
inscription that cannot be constructed is an integrity failure. The
use case rolls the transaction back. That failure is not one of the
five business sentences.

### Business authorization

When the required identifiers fail input validation, the response is
that validation result alone. FR-014 applies after those identifiers
have passed. The use case then reads `note` and any named target
student from the input contract, passes only the validated command to
domain behavior, and returns one message:

1. Grade attempt, when `note` is present.
2. Enrolling someone else, when a named target student differs from
   the acting student. The request does not accept that target as the
   student to enroll.
3. Not a registered student.
4. Course does not exist.
5. Already enrolled.

A refusal writes nothing. A success stores one inscription with no
grade.

FR-014 stays the student-visible rule. This design does not turn those
five outcomes into one validation collection.

### Outbound

Programme, student, course, and inscription ports stay
application-owned. SQLite adapters translate rows to domain objects on
the way in and write from domain values on the way out. The unit of
work owns `BEGIN IMMEDIATE`, commit, and rollback.

### Later code change

This plan does not implement the change. The later change is the input
contract, identifier value objects, the validation collection inside
the application, the HTTP 400 `errors` array, and the use case reading
the input contract for authorization while passing only the validated
command to domain behavior. Persistence, the business sentences, and
FR-014 stay.

## Verification

Follow Red, Green, Refactor for any behavior that changes. A
behavior-preserving move needs the existing tests passing before the
change and after it. Tests that already pass do not count as the Red
phase for a new behavior.

- Unit tests for domain construction, for the FR-014 order, and for an
  application result that contains two identifier errors with stable
  codes. That unit test does not assert an HTTP body.
- Integration tests for the existing single-failure HTTP sentences and
  for the SQLite uniqueness conflict.
- An import test that domain and application modules do not import
  Flask, `sqlite3`, or adapters. No new tool is required for that
  check.
- Branch coverage of new or modified `college` business code at 100%,
  using the configured pytest-cov scope. The recorded baseline is the
  100% branch result in `evidence/coverage.txt`. A later run must not
  fall below that baseline under the same scope. A file percentage
  alone does not prove a new branch ran.
- After the configuration in Static checks is installed: `ruff check src/college` and `pyright`. Fix genuine findings in `src/college`. Do not suppress a real error to make the first run pass. These checks do not replace pytest or the branch-coverage gate.
- Curl against the running process for the success and single-failure
  outcomes in the specification. The Flask test client does not
  replace that run.
- A curl that sends two business rules expects the one FR-014
  sentence. A curl that sends two invalid identifiers expects HTTP 400
  and the `errors` array in the contract.
- Completion needs the test result, the branch-coverage result, the
  Ruff result, the Pyright result, and the curl result. A green unit
  run alone is not completion.

## Static checks

Adopt Ruff and Pyright as development dependencies. pytest and branch
coverage stay. They check runtime behavior. They do not check the
typed boundary between application, domain, and infrastructure.

This feature adds validated commands and domain identity types. That
is the demonstrated need under Principle E3. The initial scope is
`src/college` only. Strict typing of the whole project, and
refactoring outside that package, are not part of this decision.

Proposed `pyproject.toml` changes, not applied until this plan is
approved:

```toml
[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "ruff", "pyright"]

[tool.ruff]
src = ["src/college"]

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]

[tool.pyright]
include = ["src/college"]
typeCheckingMode = "basic"
```

`E4`, `E7`, and `E9` are the import, statement, and runtime groups.
`F` is Pyflakes. No other Ruff rules are selected. Pyright stays in
basic mode. Versions are unpinned, as pytest and pytest-cov are today.

Verification commands, from `lab-4/` after the dev extra is installed:

```bash
ruff check src/college
pyright
```

The first passing run of those two commands is the baseline. A genuine
error in `src/college` is fixed in that module. A passing baseline
does not use a file-wide ignore, a blanket `# noqa`, or a blanket
`# type: ignore`. The pytest branch-coverage gate stays at 100% for
`college`.

## Resolved decisions

- **RF-001.** Resolved. Constitution 6.0.1 A10 accumulates independent
  input-validation failures. Business refusals stay on FR-014, one
  message, first match. No business sentence changed.
- **UD-001.** Resolved. More than one identifier failure is HTTP 400
  with an `errors` array of stable codes and field names.

No decision remains open for task generation. This plan does not
generate tasks.

## Complexity Tracking

No constitutional gate is waived.
