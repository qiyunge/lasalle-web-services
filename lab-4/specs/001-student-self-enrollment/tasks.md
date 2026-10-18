# Tasks: Student Self-Enrollment

**Input**: Design documents from `/specs/001-student-self-enrollment/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Vertical slices. Each changed behavior starts with an acceptance test from `spec.md` and `contracts/student-self-enrollment.md`. Implementation then moves from `src/college/adapters/inbound/http.py` through `src/college/application/enroll_student.py` toward domain code and outbound adapters, and only as far as that slice needs. Constitution E5 applies inside every slice. For new or changed behavior: Red, run the test and confirm it fails for the stated reason; Green, the minimum change that makes it pass while accepted tests stay passing; Refactor, structure only, then run that slice's tests again. A test that still describes accepted behavior stays. A test that expects "You can only enroll yourself." does not. Do not add authentication. Do not change the specification or the constitution.

**Organization**: Setup, a baseline of still-accepted tests, User Story 1 slices, User Story 2, then the architecture, coverage, Ruff, Pyright, and running-service gates.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Production code: `src/college/`
- Tests: `tests/unit/`, `tests/integration/`
- Paths are relative to `lab-4/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Record the approved static-check configuration. Do not change business rules.

- [X] T001 Add Ruff and Pyright to the dev extra in `pyproject.toml`. Set `[tool.ruff] src = ["src/college"]` and `[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]`. Set `[tool.pyright] include = ["src/college"]` and `typeCheckingMode = "basic"`. Leave versions unpinned. Do not switch Pyright to strict. Do not select more Ruff rules. Do not install the packages in this task.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm the tests that still match the specification before any slice changes behavior.

**⚠️ CRITICAL**: No slice starts until T002 has passed.

- [X] T002 From `lab-4/`, run the still-accepted enrollment and browse tests: `test_enroll_returns_created_inscription`, `test_student_enrolls_without_an_administrator`, `test_programme_does_not_block_enrollment`, `test_second_course_creates_a_separate_inscription`, `test_two_students_can_enroll_in_the_same_course`, `test_missing_course`, `test_incomplete_course_does_not_exist`, `test_duplicate_leaves_existing_note_unchanged`, `test_duplicate_and_existing_note`, `test_persistence_conflict_is_already_enrolled`, `test_concurrent_enrollment_keeps_one_inscription`, `test_missing_student_is_not_registered`, `test_incomplete_student_is_not_registered`, `test_missing_programme_is_not_registered`, `test_not_registered`, `test_student_without_a_programme`, `test_grade_attempt_wins_over_an_unregistered_student`, `test_grade_attempt_wins_over_a_missing_course`, `test_grade_attempt_wins_over_an_existing_inscription`, `test_unregistered_student_wins_over_a_missing_course`, `test_missing_course_wins_over_an_existing_inscription`, `test_invalid_stored_inscription_is_an_integrity_failure`, and `test_invalid_stored_inscription_is_internal_failure`, plus `tests/unit/test_browse_courses.py` and `tests/integration/test_http_courses.py`. Confirm they pass. Do not require `test_enroll_other_student`, `test_same_student_id_is_self_enrollment`, `test_grade_attempt_wins_over_enrolling_someone_else`, or `test_enrolling_someone_else_wins_over_*` to pass. Do not edit `src/college/` in this task.

**Checkpoint**: Accepted enrollment and browse tests are green. The self-only refusal tests are outside this baseline.

---

## Phase 3: User Story 1 - Enroll in a course (Priority: P1) 🎯 MVP

**Goal**: A registered acting student enrolls in an existing course. The inscription belongs to that acting student, has no grade, and is persisted. The acting student comes from the trusted caller context.

**Independent Test**: With one registered student whose programme has a nonempty name, and one existing course, a request with no target-student field and no `note` returns "You are enrolled in this course." and one grade-free inscription for that acting student.

### Slice US1-A — Successful self-enrollment

Specification User Story 1 scenarios 1 and 4. FR-004, FR-005, FR-006.

- [X] T003 [US1] Acceptance: run `test_enroll_returns_created_inscription` in `tests/integration/test_http_enrollment.py` and `test_student_enrolls_without_an_administrator` in `tests/unit/test_enroll_student.py`. The request omits `note` and any target-student field. The inscription names the acting student and the course, has no grade, and the message is "You are enrolled in this course." No administrator step exists in `src/college/adapters/inbound/http.py` or `src/college/application/enroll_student.py`. If they pass, stop with no production change. If one fails, Green from `src/college/adapters/inbound/http.py` inward; Refactor; re-run both tests.

### Slice US1-B — Programme does not block enrollment

Specification User Story 1 scenarios 2 and 5. FR-012.

- [X] T004 [US1] Acceptance: run `test_programme_does_not_block_enrollment` in `tests/unit/test_enroll_student.py`. Do not add an enrollment period, a capacity limit, a prerequisite, or a course availability status to `src/college/domain/course.py` or `src/college/application/enroll_student.py`. If it passes, stop with no production change. If it fails, Green from `src/college/application/enroll_student.py` inward; Refactor; re-run that test.

### Slice US1-C — Another course, and two students in one course

Specification User Story 1 scenarios 3 and 6. FR-013.

- [X] T005 [US1] Acceptance: run `test_second_course_creates_a_separate_inscription` and `test_two_students_can_enroll_in_the_same_course` in `tests/unit/test_enroll_student.py`. If they pass, stop with no production change. If one fails, Green from `src/college/application/enroll_student.py` inward; Refactor; re-run both tests.

### Slice US1-D — Course does not exist

Specification FR-007.

- [X] T006 [US1] Acceptance: run `test_missing_course` in `tests/unit/test_enroll_student.py` and `tests/integration/test_http_enrollment.py`, and `test_incomplete_course_does_not_exist` in `tests/unit/test_enroll_student.py`. The message is "That course does not exist." Nothing is written. If they pass, stop with no production change. If one fails, Green from `src/college/adapters/inbound/http.py` through `src/college/application/enroll_student.py` to `src/college/domain/course.py`; Refactor; re-run those tests.

### Slice US1-E — Already enrolled, including overlap

Specification FR-008.

- [X] T007 [US1] Acceptance: run `test_duplicate_leaves_existing_note_unchanged` and `test_persistence_conflict_is_already_enrolled` in `tests/unit/test_enroll_student.py`, `test_duplicate_and_existing_note` in `tests/integration/test_http_enrollment.py`, and `test_concurrent_enrollment_keeps_one_inscription` in `tests/integration/test_inscription_concurrency.py`. The message is "You are already enrolled in this course." An existing grade on that inscription is unchanged. If they pass, stop with no production change. If one fails, Green from `src/college/application/enroll_student.py` toward `src/college/adapters/outbound/sqlite_unit_of_work.py`; Refactor; re-run those tests.

### Slice US1-F — Present `note`, including null

Specification FR-011. A present `note` is a grade attempt, including null, an empty string, or any other supplied value. An omitted `note` is not.

- [X] T008 [US1] Red: add acceptance coverage in `tests/integration/test_http_enrollment.py` and `tests/unit/test_enroll_student.py` before changing production code. Post `"note": null`, `"note": ""`, and one other supplied value. Each response is 400 and "Students cannot assign, change, or remove a grade." Nothing is written. Keep `test_note_is_a_grade_attempt` and `test_grade_attempt`. The success request in `test_enroll_returns_created_inscription` omits `note` and is not a grade attempt. Run the new cases. A case that already passes stays. A case that fails does so because that present value is not treated as a grade attempt. Green only for a failing case, from `src/college/adapters/inbound/http.py` to `src/college/application/enroll_student.py`. Refactor without changing the outcome, then re-run those tests.

### Slice US1-G — Unsupported target-student field

Specification FR-010. This replaces the business refusal "You can only enroll yourself." Do not add another business sentence and do not add authentication.

- [X] T009 [US1] Red: replace `test_enroll_other_student` and `test_same_student_id_is_self_enrollment` before changing production code. In `tests/integration/test_http_enrollment.py`, a present `student_id` that differs from `acting_student_id`, and a present `student_id` equal to `acting_student_id`, each return HTTP 400 and an `errors` array containing `{"code": "target_student_not_accepted", "field": "student_id"}`. Nothing is written. The body has no business `message`. In `tests/unit/test_enroll_student.py`, assert that same code and field for both values, and assert that no inscription is written. Delete the expectation "You can only enroll yourself." Run the tests and confirm they fail because the service still enrolls the equal id and still returns that removed sentence for a different id.

- [X] T010 [US1] Red: in `tests/unit/test_enroll_student.py`, add a failing test that a present `student_id` together with a present `note` returns only `target_student_not_accepted` and does not return "Students cannot assign, change, or remove a grade." Replace `test_grade_attempt_wins_over_enrolling_someone_else` and `test_enrolling_someone_else_wins_over_*` so they no longer expect "You can only enroll yourself." Keep `test_grade_attempt_wins_over_an_unregistered_student`, `test_grade_attempt_wins_over_a_missing_course`, `test_grade_attempt_wins_over_an_existing_inscription`, `test_unregistered_student_wins_over_a_missing_course`, and `test_missing_course_wins_over_an_existing_inscription`. Run the new test and confirm it fails because business evaluation still runs while the target-student field is present.

- [X] T011 [US1] Green from the boundary: change `src/college/adapters/inbound/http.py` and `src/college/application/enroll_student.py` by the minimum that makes T009 and T010 pass. A supplied target-student field is an input-validation error. It is accumulated with other independent input-validation errors and is not a business refusal. Input validation finishes before FR-014. The acting student on a success is the trusted-context student. Do not pass the Flask request into `enroll`. Refactor those two modules without changing this behavior, then re-run `tests/unit/test_enroll_student.py` and `tests/integration/test_http_enrollment.py`.

### Slice US1-H — Four-step business refusal order

Specification FR-014. Order: a grade attempt; then the acting student is not registered; then the course does not exist; then the student is already enrolled.

- [X] T012 [US1] Acceptance: run the remaining `wins_over` tests in `tests/unit/test_enroll_student.py`. One attempt that matches more than one business refusal, and that has no input-validation error, returns only the earlier sentence. A grade attempt by an unregistered student is "Students cannot assign, change, or remove a grade." If they pass, stop with no production change. If one fails, Green in `src/college/application/enroll_student.py`; Refactor; re-run that file.

### Slice US1-I — Programme without a nonempty name

Specification FR-009 and `data-model.md`. A programme needs an integer `id` and a nonempty `name`. Nonempty means at least one character. This feature does not define removal of surrounding spaces. Names are not required to be unique. A record that lacks either value is not an existing programme.

- [X] T013 [US1] Red: add a failing acceptance test in `tests/integration/test_http_enrollment.py` before changing production code. An otherwise complete acting student refers to a programme that has no nonempty name. The response is 400 and "Only a registered student can enroll in a course." No inscription is stored. On the current table, a programme row that stores only `id` has no name. Run the test and confirm it fails because that student is enrolled.

- [X] T014 [US1] Add a unit test in `tests/unit/test_enroll_student.py` that a programme-port failure is that same sentence and writes nothing. Run it. If it already passes, leave `src/college/application/enroll_student.py` unchanged in this task. If it fails, Green only that mapping, then Refactor and re-run the new unit test. Do not add the programme name type in this task.

- [X] T015 [US1] Red: write failing tests in `tests/unit/test_programme.py` before changing `src/college/domain/programme.py`. `Programme.create` returns `Failure` and does not raise when `id` is not an integer, including a boolean, or when `name` is missing or empty. The same invalid values passed to `Programme(...)` raise `ConstructionError` and return no programme. A valid `create` returns `Success` holding a `Programme`. Keep the existing rejection of a non-integer `id`. Run the file and confirm the new name cases fail because the type still accepts an identifier alone.

- [X] T016 [US1] Green: implement the minimum `Programme.create` and `Programme.__post_init__` in `src/college/domain/programme.py` so T015 passes. Use the standard library only. `create` returns `Failure` without raising and calls the constructor only after the value is valid. Do not add a user-facing sentence in this module. Where a valid in-memory `Programme` is built in `tests/unit/test_enroll_student.py` or `tests/integration/test_http_enrollment.py`, pass a nonempty name and leave the enrollment assertions unchanged. Refactor `src/college/domain/programme.py` without changing this behavior, then re-run `tests/unit/test_programme.py` and `tests/unit/test_enroll_student.py`.

- [X] T017 [US1] Red: write failing tests in `tests/integration/test_persisted_records.py` before changing the programme repository. A missing programme row returns `Failure(Missing)`. A stored row whose name is empty or missing returns `Failure` and does not return a `Programme`. A stored row with an integer `id` and a nonempty `name` returns `Success(Programme)`. Update the existing present-programme expectation so the expected programme includes a nonempty name. Run the test and confirm it fails because `src/college/adapters/outbound/sqlite_programme_repository.py` still selects only `id`.

- [X] T018 [US1] Green, continuing inward from T013: update `initialize_schema` in `src/college/adapters/outbound/sqlite_unit_of_work.py` so `programme` stores `id` and `name`. `CREATE TABLE IF NOT EXISTS` does not add a column to an existing table, so use a new database file for checks created with the old table. Change `get` in `src/college/adapters/outbound/sqlite_programme_repository.py` to construct `Programme` from the stored `id` and `name` and to return the domain `Failure` unchanged. Update `seed_development` in `src/college/app.py` so programme 1 has a nonempty name. Give the existing `INSERT INTO programme (id)` statements in `tests/integration/test_http_enrollment.py`, `tests/integration/test_persisted_records.py`, and `tests/integration/test_inscription_concurrency.py` a nonempty name, and point the T013 case at a programme whose name is empty. Keep `test_invalid_stored_inscription_is_an_integrity_failure` and `test_invalid_stored_inscription_is_internal_failure`. Run T013 and T017 and confirm they pass. Refactor the repository and schema setup without changing this behavior, then re-run those integration files and `tests/unit/test_enroll_student.py`.

**Checkpoint**: Success, the grade sentence, the target-student validation error, and the programme-name refusal are independently testable.

### Slice US1-J — Accumulated input validation

Plan and constitution A10. Identifier value objects are introduced only in this slice. Validation still finishes before FR-014.

- [X] T019 [US1] Red: add failing acceptance tests in `tests/integration/test_http_enrollment.py` before moving the remaining identifier checks. One missing `acting_student_id`, with no target-student field, stays 400 and "acting_student_id is required." One missing `course_id` stays 400 and "course_id is required." One non-integer identifier, including a boolean, stays 400 and "acting_student_id and course_id must be integers." A body that is not a JSON object, a body missing both required identifiers, and a body that combines a target-student field with an identifier failure return 400 and an `errors` array. Each element has `code` and `field`. `acting_student_id` comes before `course_id`, and `target_student_not_accepted` follows those identifier errors. A missing field is not also reported as not an integer. The identifier codes are `acting_student_id_missing`, `course_id_missing`, `acting_student_id_not_integer`, and `course_id_not_integer`. When any of these validation errors is present, the body does not include a business sentence. Run the new tests and confirm the multiple-error case fails because the adapter still returns the first shape sentence.

- [X] T020 [US1] Red: add failing tests in `tests/unit/test_enroll_student.py` before changing the collection behavior. Assert the application result, not an HTTP body. Both required identifiers missing produces a non-empty collection containing `acting_student_id_missing` and `course_id_missing`, and nothing is written. One missing identifier produces only that identifier's code. A target-student field is included in that same collection. The grade sentence is decided only after validation has produced no errors. Run the new tests and confirm they fail because `enroll` still stops at the first raw identifier.

- [X] T021 [US1] Red: write failing tests in `tests/unit/test_identifiers.py` before adding `src/college/domain/identifiers.py`. An acting-student identifier and a course identifier each accept an integer and reject a missing value, a boolean, and any other non-integer. Construction of an invalid identifier returns no valid instance. Run the file and confirm it fails because the module does not exist.

- [X] T022 [US1] Green: implement the minimum identifier types in `src/college/domain/identifiers.py` so T021 passes. Use the standard library only. Do not import Flask, `sqlite3`, or an adapter. Refactor that module without changing this behavior, then re-run `tests/unit/test_identifiers.py`.

- [X] T023 [US1] Green from the boundary: change `src/college/adapters/inbound/http.py` so it builds the input contract and maps the application outcome. It does not decide the grade sentence and it does not repeat the identifier checks. One required-identifier failure, with no target-student field, keeps the existing `message` sentence. Any `target_student_not_accepted` error, and more than one identifier failure, returns the `errors` array from `contracts/student-self-enrollment.md`. Do not pass the Flask request into `enroll`. Change `src/college/application/enroll_student.py` by the minimum that makes T020 pass. Build a validated command only from the acting-student and course identifier types in `src/college/domain/identifiers.py`. Do not put a target-student field or `note` on that command. Collect every independent input-validation failure. Do not stop at the first. Ask the domain type to accept or reject an identifier, and do not copy that rule. After validation produces no errors, apply the four-step FR-014 order and return one business message. A refusal writes nothing. Refactor those two modules without changing this behavior, then re-run `tests/unit/test_enroll_student.py` and `tests/integration/test_http_enrollment.py`.

**Checkpoint**: User Story 1 acceptance tests pass, including target-student validation, present `note`, the programme-name refusal, and the four-step FR-014 order.

---

## Phase 4: User Story 2 - Browse available courses (Priority: P2)

**Goal**: A registered student sees every existing course. Programme name does not add or remove a course.

**Independent Test**: `GET /courses` returns 200 and the set of existing courses, each with an identifier, a course code, and a name. A course that lacks a nonempty code or a nonempty name is absent. An empty catalogue returns an empty list. Course order is not a requirement.

### Slice US2-A — Course list

Specification User Story 2 scenarios 1 through 6. FR-001, FR-002, FR-003.

- [X] T024 [P] [US2] Acceptance: run `tests/unit/test_browse_courses.py` and `tests/integration/test_http_courses.py`. Cover every existing course, a course outside the student's programme, a course the student is already enrolled in, an empty list, two courses that share a name, and a course record with no course code or no name. This browse behavior is unchanged. Do not filter courses by programme in `src/college/application/browse_courses.py` or `GET /courses` in `src/college/adapters/inbound/http.py`. If a fixture still inserts a programme without a nonempty name, add that name and leave the browse assertions unchanged. If the tests pass, stop with no production change. If a listed scenario fails, Green from `src/college/adapters/inbound/http.py` to `src/college/application/browse_courses.py`; Refactor; re-run both files.

**Checkpoint**: Browse and enrollment both pass their own test files.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Architecture, coverage, static checks, and the running service.

- [X] T025 [P] Add `tests/unit/test_architecture_boundaries.py`. Assert that modules under `src/college/domain/` and `src/college/application/` do not import Flask, `sqlite3`, or `college.adapters`. Run the file and confirm it passes. Do not move a business rule into an adapter to make it pass.

- [X] T026 From `lab-4/`, run `python -m pytest -v --cov=college --cov-branch --cov-report=term-missing`. Keep the configured gate `--cov=college --cov-branch --cov-fail-under=100` from `pyproject.toml`. New or modified business branches in `src/college` are covered at 100% branch coverage. The baseline is the recorded 100% branch result in `specs/001-student-self-enrollment/evidence/coverage.txt`, measured on that same scope, and this run must not fall below it. A file percentage alone does not prove a new branch ran. Do not add an omit, a pragma, a lower threshold, or a test exclusion. Do not weaken, delete, skip, or rewrite a test to satisfy the gate. If a new business branch has no test, return to Red on that slice, make the minimum change, refactor without changing behavior, and run this command again.

- [X] T027 Install the dev extra, then run `ruff check src/college` and `pyright` from `lab-4/`. Fix genuine findings in `src/college`. Do not add a file-wide ignore, a blanket `# noqa`, or a blanket `# type: ignore`. Do not change Pyright to strict and do not select more Ruff rules. The first passing pair of runs is the baseline. These checks do not replace the coverage gate.

- [X] T028 Run the curl sequence in `specs/001-student-self-enrollment/quickstart.md` against the running application, not the Flask test client. Include the course list, success for the acting student with `note` omitted, duplicate, missing course, a present `note` including null, a `student_id` equal to the acting student, an acting student whose programme has no nonempty name, one identifier failure, and two identifier failures. Two business rules still expect the one four-step FR-014 sentence. A target-student field and two identifier failures expect HTTP 400 and the `errors` array.

---

## Phase 6: Domain Design Refactor (A2, A4, A5, A9)

**Purpose**: Behavior-preserving refactor. Existing tests pass before and after. Only the new domain service is new behavior and starts Red.

- [X] T029 Red: add `tests/unit/test_self_enrollment.py` for the domain service. It covers each refusal, the FR-014 first-match order, the requirement that the programme is the student's own, a corrupt stored inscription returned to the caller, and a new inscription that is stored without a grade. Run it and confirm it fails because the module and `ProgrammeId` do not exist.
- [X] T030 Green: add `ProgrammeId` and a shared identifier base in `src/college/domain/identifiers.py`. Add `src/college/domain/self_enrollment.py` with `Refusal` and `decide_self_enrollment`. Add `NewInscription` to `src/college/domain/inscription.py`. `Programme`, `Student`, `Course`, and `Inscription` hold identifier value objects. Their `create` factories reconstitute from stored primitives. Make `Success` and `Failure` generic.
- [X] T031 Refactor the application: `SelfEnrollmentRequest` input contract, `EnrollInCourse` validated command of domain types, typed `EnrollmentPorts`, and outcomes that do not use HTTP vocabulary. The use case loads facts and delegates the decision to the domain service. Outbound ports take identifier value objects. `InscriptionPort.add` stores a `NewInscription`, so the adapter does not decide the note.
- [X] T033 Student lifecycle: replace `Student.create`, which took raw primitives and re-checked identifiers, with `Student.reconstitute`, which takes `StudentId` and `ProgrammeId`. `SqliteStudentRepository` builds both through their `create` factories and returns `InvalidStudent` when either fails. Red: entity tests for `reconstitute`. Adapter tests for an invalid stored programme identifier and a valid row. Then Green and Refactor.
- [X] T032 Update test doubles and fixtures to domain types without changing what each test asserts. Re-run pytest with branch coverage, `ruff check src/college`, `pyright`, and the curl sequence against the running application.
- [X] T034 Controlled reimplementation of all `src/college` modules from the spec, plan, and constitution. Add an `Email` value object and `InscriptionId`. All entities take value objects; `reconstitute` replaces every raw `create` factory; `NewInscription.stored_as(InscriptionId)` yields the stored inscription. Adapters convert columns that can hold bad data through value-object `create` factories at the row boundary. Red: value-object and `reconstitute` tests, with fixtures moved to domain types and assertions unchanged. Then Green, Refactor, and every gate: pytest with branch coverage, `ruff check`, `pyright`, the architecture-boundary tests, and the curl sequence.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. T001 does not block the tests.
- **Foundational (Phase 2)**: Depends on the current tree. Blocks every slice.
- **User Story 1 (Phase 3)**: Depends on T002. Slices US1-A through US1-E finish before US1-F. US1-F finishes before US1-G. US1-G finishes before US1-H. US1-H finishes before US1-I. US1-I finishes before US1-J.
- **User Story 2 (Phase 4)**: Depends on T002. It does not depend on the enrollment slices.
- **Polish (Phase 5)**: Depends on T023 and T024. T027 follows T001. T028 follows T023.

### User Story Dependencies

- **User Story 1 (P1)**: Its demo checkpoint is T018. Its completion checkpoint is T023.
- **User Story 2 (P2)**: Its checkpoint is T024.

### Within Each Slice

- The acceptance test is the first task of a changed slice.
- New behavior stays Red until the inward Green task.
- Domain types and adapters are added only in the slice that needs them. Programme name appears in US1-I. Identifier value objects appear in US1-J.
- Each Green task ends with Refactor and a fresh run of that slice's tests.

### Parallel Opportunities

- T024 can run beside US1-A through US1-H because it uses the browse test files.
- T025 can run beside T026 after the story slices pass.
- US1 slices that edit `tests/integration/test_http_enrollment.py` stay in order.

---

## Parallel Example: User Story 2

```bash
# After T002, browse acceptance does not wait for the enrollment slices:
Task: "T024 acceptance tests in tests/unit/test_browse_courses.py and tests/integration/test_http_courses.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 through the programme-name slice)

1. Complete T002.
2. Complete US1-A through US1-H. Preserved slices stop when their accepted tests pass. US1-F and US1-G change `note` and target-student behavior.
3. Complete US1-I. Stop and validate success, the grade sentence, `target_student_not_accepted`, and the programme-name refusal.

### Incremental Delivery

1. US1-J moves the remaining identifier checks inward and accumulates independent validation errors before FR-014.
2. User Story 2 confirms the course list.
3. T025 through T028 enforce the architecture, coverage, Ruff, Pyright, and running-service gates.

---

## Notes

- [P] tasks use different files and do not depend on an unfinished task.
- Exact business sentences stay those in `specs/001-student-self-enrollment/spec.md`.
- FR-014 order is: a grade attempt; then the acting student is not registered; then the course does not exist; then the student is already enrolled.
- "You can only enroll yourself." is not a business refusal. A supplied `student_id`, including one equal to the acting student, is `target_student_not_accepted`.
- A present `note`, including null, an empty string, or any other supplied value, is a grade attempt. An omitted `note` is not.
- Do not install Ruff or Pyright before T027. T001 only edits `pyproject.toml`.
