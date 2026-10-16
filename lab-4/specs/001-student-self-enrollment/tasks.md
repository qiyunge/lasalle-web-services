# Tasks: Student Self-Enrollment

**Input**: Design documents from `/specs/001-student-self-enrollment/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required. Genuinely new or changed behavior is Red, then Green, then Refactor. A Red task is done only after the new test has been run and has failed for the missing behavior. A Green task is done only after that same test has been run and passed. A test that passes on its first run is not a Red cycle. Do not change production code to force that failure. FR-014 combination coverage is characterization: run it and record the natural result. Do not delete, weaken, skip, or exclude a test to make a run pass.

**Organization**: Brownfield. The current `src/college/` service and `tests/` stay. Tasks add the finalized plan on top of that behavior.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Paths are relative to `lab-4/`
- Application code is under `src/college/`
- Tests are under `tests/unit/` and `tests/integration/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing suite before any behavior change

- [ ] T001 Run `python -m pytest -v` from `lab-4/` against the existing `tests/` and `src/college/` tree and confirm it passes before any edit. Do not modify `src/`, `tests/`, `pyproject.toml`, or the specification.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: `Result` and constructor enforcement. This phase does not switch the outbound port contracts.

**⚠️ CRITICAL**: User story work waits until T011 has passed. T011 is not a full-suite checkpoint. After the constructors enforce invariants, some existing tests error because they still build an invalid entity or load an invalid row. Leave those tests in place until the migration tasks name them.

### Red

- [ ] T002 [P] Write failing tests in `tests/unit/test_student_factory.py`. `Student.create` with an empty or missing name, or an empty or missing email, returns `Failure(InvalidStudent)` and does not raise. `id` and `programme_id` must be integers. Name and email must be nonempty strings. `Student(1, "", "ada@college.test", 1)` raises `ConstructionError` and does not return a student. A valid `create` returns `Success` holding a `Student`. Run this file and confirm it fails because that construction path does not yet enforce the invariant.

- [ ] T003 [P] Write failing tests in `tests/unit/test_course_factory.py`. `Course.create` returns `Failure(InvalidCourse)` when `id` is not an integer or when course code or name is not a nonempty string, and it does not raise. `Course(10, "", "Introduction")` raises `ConstructionError` and does not return a course. A valid `create` returns `Success` holding a `Course`. Run this file and confirm it fails because that construction path does not yet enforce the invariant.

- [ ] T004 [P] Write failing tests in `tests/unit/test_programme.py`. `Programme(1)` returns a programme. `Programme(None)` raises `ConstructionError` and does not return a programme. Do not add an `InvalidProgramme` outcome or a `Programme.create` factory. Run this file and confirm the invalid call does not yet fail closed.

- [ ] T005 [P] Write failing tests in `tests/unit/test_inscription_factory.py`. `Inscription.create` returns `Failure(InvalidInscription)` and does not raise when `id`, `student_id`, or `course_id` is not an integer, or when `note` is neither `None` nor a string. `note` of `None` or `"A"` is valid. The factory does not check that the student or the course exists and does not apply a grade range. The same invalid arguments passed to `Inscription(...)` raise `ConstructionError` and do not return an inscription. Run this file and confirm it fails because that construction path does not yet enforce the invariant.

### Green

- [ ] T006 Add `Success`, `Failure`, and `ConstructionError` in `src/college/domain/result.py`, using the standard library only. `Success` carries the entity. `Failure` carries one error value and no user-facing sentence. Do not implement the entity checks in this task.

- [ ] T007 [P] Implement `Student.create` and `Student.__post_init__` in `src/college/domain/student.py` so T002 passes. `create` returns `Failure` without raising. It calls the constructor only after the value is valid. The constructor raises `ConstructionError` for the same breach.

- [ ] T008 [P] Implement `Course.create` and `Course.__post_init__` in `src/college/domain/course.py` so T003 passes. Use the same `Failure` versus `ConstructionError` split as `Student`.

- [ ] T009 [P] Enforce `id` is an integer in `Programme.__post_init__` in `src/college/domain/programme.py` so T004 passes. Do not add a factory or a `Result` failure type for a programme.

- [ ] T010 [P] Implement `Inscription.create` and `Inscription.__post_init__` in `src/college/domain/inscription.py` so T005 passes. A stored grade string remains valid.

- [ ] T011 Run `tests/unit/test_student_factory.py`, `tests/unit/test_course_factory.py`, `tests/unit/test_programme.py`, and `tests/unit/test_inscription_factory.py` and confirm they pass. Do not use `python -m pytest` as this task's gate. These existing tests may now error, and they stay unchanged until the task that names them: incomplete student and course cases in `tests/unit/test_enroll_student.py` (T015), the incomplete-course case in `tests/unit/test_browse_courses.py` (T026), and the blank `course_code` row in `tests/integration/test_http_courses.py` (T026). Do not delete, skip, weaken, or exclude them, and do not add a pytest ignore.

**Checkpoint**: The four new factory files pass. The full suite is not green yet. The get/find migration in User Story 1 is the next work, and it does not end with a full-suite pass.

---

## Phase 3: User Story 1 - Enroll in a course (Priority: P1) 🎯 MVP

**Goal**: A registered student enrolls without an administrator. Refusals keep the FR-014 order and the existing sentences. An invalid stored inscription is an integrity failure, not a business refusal.

**Independent Test**: With one registered student and one existing course, enrollment returns "You are enrolled in this course." and one grade-free inscription. Each single refusal returns its existing sentence and writes nothing. Combined business refusals return the earliest FR-014 sentence and write nothing. `Failure(InvalidInscription)` rolls back and returns HTTP 500. Run the enrollment files named in T024. Browse tests are not this story's gate.

### Migration: get/find port, adapters, and enroll

T013, T014, and T015 are one migration. The port signatures, the production adapters that implement them, and `enroll` plus its unit-test fakes all agree before any later task treats the suite as green. No task in this migration is complete because `python -m pytest` passed. `CoursePort.list_all` stays on its current return value until User Story 2.

#### Red

- [ ] T012 [US1] Add failing repository tests in `tests/integration/test_persisted_records.py`. A stored student with an empty name makes `SqliteStudentRepository.get` return `Failure(InvalidStudent)`, not a `Student`. A missing student row returns `Failure(Missing)`. A stored course with an empty course code makes `SqliteCourseRepository.get` return `Failure(InvalidCourse)`. `SqliteProgrammeRepository.get` returns `Success(Programme)` or `Failure(Missing)` and constructs `Programme(id)` with no factory. When `Inscription.create` would fail, `SqliteInscriptionRepository.find` returns that `Failure` unchanged. Run the file and confirm it fails because the repositories still build unchecked entities.

#### Port, adapters, then consumer

- [ ] T013 [US1] In `src/college/application/ports.py`, add `Missing` and the `CourseList` type. `Missing` means no row. `CourseList` holds the valid `Course` entities and the `InvalidCourse` diagnostics from one read, without copying course fields into another object. `StudentPort.get` and `CoursePort.get` return `Success(entity)`, `Failure(Missing)`, or `Failure(InvalidStudent)` / `Failure(InvalidCourse)`. `ProgrammePort.get` returns `Success(Programme)` or `Failure(Missing)`. `InscriptionPort.find` returns `Success(Inscription)`, `Failure(Missing)`, or `Failure(InvalidInscription)`. Leave `CoursePort.list_all` returning its current collection until T026. Do not run the full suite. This task is incomplete until T014 and T015 have landed.

- [ ] T014 [US1] Change `get` in `src/college/adapters/outbound/sqlite_student_repository.py`, `src/college/adapters/outbound/sqlite_programme_repository.py`, and `src/college/adapters/outbound/sqlite_course_repository.py`, and change `find` in `src/college/adapters/outbound/sqlite_inscription_repository.py`, so T012 passes. A missing row is `Failure(Missing)`. A present student, course, or inscription row is the factory `Result`, returned unchanged. A programme row is `Programme(id)`. Do not choose a user-facing sentence in these files. Leave `list_all` unchanged. Run only `tests/integration/test_persisted_records.py` and confirm it passes. Do not run the full suite. `tests/integration/test_http_courses.py` may still error on the blank `course_code` row because `list_all` still constructs a `Course`. Leave that test unchanged.

- [ ] T015 [US1] Update `src/college/application/enroll_student.py` and the fakes in `tests/unit/test_enroll_student.py` so an incomplete stored student or course is a `Failure` from the port, not an invalid constructed entity. Keep every existing assertion, including "Only a registered student can enroll in a course." and "That course does not exist." Map `Failure(Missing)` and `Failure(InvalidStudent)`, and a missing programme, to "Only a registered student can enroll in a course." Map `Failure(Missing)` and `Failure(InvalidCourse)` to "That course does not exist." Map `Success(Inscription)` to "You are already enrolled in this course." `Failure(Missing)` from `find` still continues to `add`. Do not implement outcome `integrity` in this task. Do not edit `tests/unit/test_browse_courses.py` or `tests/integration/test_http_courses.py`. Run `tests/unit/test_enroll_student.py`, `tests/integration/test_http_enrollment.py`, `tests/integration/test_persisted_records.py`, `tests/integration/test_development_seed.py`, and `tests/integration/test_inscription_concurrency.py`. Do not require the full suite, and do not exclude the browse tests that still fail.

### Characterization and gap verification

- [ ] T016 [US1] Add combination tests to `tests/unit/test_enroll_student.py` and run them. This task is characterization and gap verification of the refusal order, not a Red task. One attempt that matches more than one rule returns only the earliest sentence and writes nothing. The order is a grade attempt ("Students cannot assign, change, or remove a grade."); then enrolling someone else ("You can only enroll yourself."); then the person is not a registered student ("Only a registered student can enroll in a course."); then the course does not exist ("That course does not exist."); then the student is already enrolled ("You are already enrolled in this course."). Cover a grade attempt combined with each later rule, enrolling someone else combined with each later rule, an unregistered student combined with a missing course, and a missing course combined with an existing inscription for that pair. Keep the existing grade-over-other-student test. Record whether the run passes or fails. Do not modify `src/college/application/enroll_student.py` in this task. Do not change an input or an assertion to produce a failure.

- [ ] T017 [US1] If T016 recorded a failure, change only the refusal order in `src/college/application/enroll_student.py` until those same tests pass, then run them again and record the pass. If T016 recorded a pass, do not modify `src/college/application/enroll_student.py`. Do not remove a refusal test.

### Red

- [ ] T018 [US1] Add a failing test in `tests/unit/test_enroll_student.py` where `find` returns `Failure(InvalidInscription)` after the earlier business checks have passed. Expect outcome `integrity`, message "Stored inscription data is invalid.", no call to `add`, and a call to `rollback` on the unit of work. A grade attempt in the same request still returns the grade sentence and does not reach this result. Run the test and confirm it fails because `enroll` does not yet treat this as an integrity failure.

- [ ] T019 [P] [US1] Add a failing HTTP test in `tests/integration/test_http_enrollment.py` that builds the blueprint with a port whose `find` returns `Failure(InvalidInscription)`. Expect status 500, body message "Stored inscription data is invalid.", and no `inscription` field. The response must not be an FR-014 sentence. Run the test and confirm it fails because `src/college/adapters/inbound/http.py` does not yet map outcome `integrity`.

- [ ] T020 [P] [US1] Add a failing test in `tests/integration/test_persisted_records.py` that opens `SqliteUnitOfWork`, calls `rollback`, and asserts the transaction does not commit. Run the test and confirm it fails because `src/college/adapters/outbound/sqlite_unit_of_work.py` does not yet roll back on that call.

### Green

- [ ] T021 [US1] Add `rollback` to `src/college/adapters/outbound/sqlite_unit_of_work.py` so T020 passes. `__exit__` rolls back and does not commit when `rollback` was called or when the block raised. A clean exit still commits. `PersistenceConflict` stays raised from `src/college/adapters/outbound/sqlite_inscription_repository.py`. Re-run the T020 test and confirm it passes.

- [ ] T022 [US1] Finish the `Failure(InvalidInscription)` path in `src/college/application/enroll_student.py` so T018 passes. Do not call `add`. Call `rollback`. Return outcome `integrity` with message "Stored inscription data is invalid." and no inscription. A business `Failure` for a student or course does not call `rollback`. `PersistenceConflict` is still handled outside the unit of work as the already-enrolled outcome. Re-run the T018 test and the T016 combination tests and confirm they pass.

- [ ] T023 [US1] Map outcome `integrity` to 500 in `src/college/adapters/inbound/http.py` so T019 passes. Before moving the shape checks, run the existing HTTP tests in `tests/integration/test_http_enrollment.py` that cover "acting_student_id is required.", "course_id is required.", and "acting_student_id and course_id must be integers." and confirm they pass. Then move those three checks out of `src/college/application/enroll_student.py` and into this adapter, before `enroll` is called. Keep those sentences. A present `note`, including JSON null, stays an application grade decision. Relocate any unit assertion that expected `enroll` to return a shape sentence onto `tests/integration/test_http_enrollment.py`. Do not delete those assertions. Run the HTTP enrollment tests again, including T019, and confirm they pass.

- [ ] T024 [US1] Run `tests/unit/test_enroll_student.py`, `tests/integration/test_http_enrollment.py`, `tests/integration/test_persisted_records.py`, `tests/integration/test_development_seed.py`, and `tests/integration/test_inscription_concurrency.py`. Confirm they pass. Do not treat `python -m pytest` as this checkpoint. `tests/unit/test_browse_courses.py` and `tests/integration/test_http_courses.py` are still allowed to fail until T026, and they stay in the tree.

**Checkpoint**: User Story 1 is independently testable through the enrollment files in T024. The full suite is not the gate. Browse still uses the previous course list.

---

## Phase 4: User Story 2 - Browse available courses (Priority: P2)

**Goal**: A registered student sees every existing course. An invalid stored course stays on the application batch and is absent from the HTTP list.

**Independent Test**: `GET /courses` returns 200 and the set of valid courses, each with `id`, `course_code`, and `name`, including a shared name and a course outside the caller's programme. An incomplete stored course is not in the JSON list. The application `CourseList.invalid` still contains that row's `InvalidCourse`. An empty catalogue returns `"courses": []`. The blank-code row already asserted by `tests/integration/test_http_courses.py` stays omitted.

### Red

- [ ] T025 [US2] Add `test_invalid_stored_course_stays_on_the_batch` to `tests/unit/test_browse_courses.py`. The fake read contains one valid `Course` and one `InvalidCourse` diagnostic, without calling `Course(...)` on an empty or missing code or name. Expect the shown list to omit that course and `CourseList.invalid` to keep the diagnostic. Keep the existing incomplete-course test in this file even if constructing `Course(1, "", "Introduction")` now raises. Run only `tests/unit/test_browse_courses.py::test_invalid_stored_course_stays_on_the_batch` and confirm it fails because browse does not yet return both parts of `CourseList`. Do not use the constructor error in the older test as this Red result. Do not delete that older test. The HTTP omission of a blank `course_code` is existing behavior; do not change production code in this task to make `tests/integration/test_http_courses.py` fail.

### Green

- [ ] T026 [US2] Change `CoursePort.list_all` in `src/college/application/ports.py` so it returns `CourseList`. Change `list_all` in `src/college/adapters/outbound/sqlite_course_repository.py` to append each `Course.create` success to `courses` and each `InvalidCourse` to `invalid`. Do not drop an invalid row and do not raise `ConstructionError` for that row. Change `src/college/application/browse_courses.py` to return that `CourseList`, with the existing `course_code` sort applied only to the valid courses. Change `GET /courses` in `src/college/adapters/inbound/http.py` to serialize `courses` only. In `tests/unit/test_browse_courses.py`, stop constructing a `Course` with an empty or missing code or name; represent those rows as `InvalidCourse` diagnostics and keep the assertion that they are absent from the shown list. Leave the blank `course_code` insert and the omission assertion in `tests/integration/test_http_courses.py` in place. The HTTP body has no diagnostic field. Run `tests/unit/test_browse_courses.py` and `tests/integration/test_http_courses.py` and confirm they pass, including T025.

- [ ] T027 [US2] Run `python -m pytest` from `lab-4/` and confirm the full suite passes. This is the first full-suite Green checkpoint after T001. It is valid only because T014, T015, and T026 have made the production adapters and consumers compatible with the port contracts. Do not exclude a test. Confirm the User Story 1 files from T024 still pass.

**Checkpoint**: Browse and enrollment both pass. The HTTP course list is still the set of valid courses.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Refactor, then measure coverage on a trusted report, then check boundaries, concurrency, and the running service

- [ ] T028 Refactor only unused helpers in `src/college/domain/`, `src/college/application/`, and `src/college/adapters/`. Run `python -m pytest` before the cleanup and again after it. If nothing is unused, leave the code in place. Do not delete or weaken a test.

- [ ] T029 Produce a trusted branch-coverage report for package `college` without editing `pyproject.toml`. The 2026-10-15 pytest-cov run is not trusted: it warned that module `college` was previously imported and not measured, and `student.py` and `course.py` showed 0 branches. Discard any report that still contains "previously imported, but not measured". From `lab-4/`, in a fresh process, run `python -m coverage erase`, then `python -m coverage run --branch --source=college -m pytest -o addopts= -p no:cov`, then `python -m coverage report -m --fail-under=100`. That sequence starts measurement before `college` is imported. `-o addopts=` avoids a second pytest-cov start; `--fail-under=100` on the report keeps the configured threshold. `[tool.coverage.run]` already sets branch coverage, `source = ["college"]`, and `omit = ["tests/*"]`. Do not add an omit, a pragma, or an exclusion, and do not lower the threshold. A trusted report has no measurement warning, exits 0 under `--fail-under=100`, and shows real branch counts for files that contain conditionals, including `src/college/domain/student.py` and `src/college/domain/course.py`. A clean-process file that contains a conditional and still shows 0 branches is a measurement failure; do not use that report.

- [ ] T030 Read only the trusted report from T029 and judge two separate results. For new or modified business code, the branch table must show every branch executed in `src/college/domain/student.py`, `src/college/domain/course.py`, `src/college/domain/programme.py`, `src/college/domain/inscription.py`, `src/college/application/enroll_student.py`, `src/college/application/browse_courses.py`, and the repository branches that map a row to `Success` or `Failure`. A file-level percentage does not satisfy this check. Separately, record the overall branch total for package `college` under the same scope: source `college`, branch coverage, omit `tests/*` only. That overall total is not the incremental check. The warned 2026-10-15 total is not the baseline. This task does not adopt a new baseline and does not change `pyproject.toml`. The configured `--cov-fail-under=100` from T029 still applies to the package measurement. If either the new-or-modified branch table or the configured package gate fails, fix the untested behavior with a new Red then Green cycle. Do not add an omit or lower the threshold.

- [ ] T031 Run the architecture checks from `specs/001-student-self-enrollment/quickstart.md` against `src/college/domain`, `src/college/application`, `src/college/adapters/inbound`, and `src/college/app.py`. Domain and application must not import Flask or `sqlite3`. The inbound adapter must not import an outbound adapter. SQLite adapter construction must appear only in `src/college/app.py`.

- [ ] T032 Run `tests/integration/test_inscription_concurrency.py` and confirm one inscription remains for the overlapping pair, the existing note is unchanged, and the losing attempt receives "You are already enrolled in this course."

- [ ] T033 Run the live curl sequence in `specs/001-student-self-enrollment/quickstart.md` against `flask --app college.app` on a fresh seeded database. Confirm the documented statuses and sentences for browse, creation, duplicate, the second student, the missing course, the unregistered student, enrolling someone else, the grade attempt, the combined grade attempt, and the three shape sentences. Do not curl an invalid inscription. The seed has no such row. That case is T018 and T019.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001. Blocks both user stories. Its gate is T011, the four factory files, not the full suite.
- **User Story 1 (Phase 3)**: Depends on T011. Does not depend on User Story 2.
- **User Story 2 (Phase 4)**: Depends on T011 and on T014. T014 edits `get` in `src/college/adapters/outbound/sqlite_course_repository.py`. T026 edits `list_all` in that same file, so it follows T014.
- **Polish (Phase 5)**: Depends on T027. T029 before T030. T028 before T029 so the report measures the refactored code.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after T011. The get/find migration is T012, then T013, then T014, then T015, with no full-suite Green checkpoint between those four. Enrollment is then testable through T024 without a passing browse suite.
- **User Story 2 (P2)**: Starts after T014 for the course repository file, and after T013 for the `CourseList` type. It does not require a successful enrollment call. Its tests use stored courses. The first full-suite pass after T001 is T027, when `list_all`, browse, and HTTP match the port.

### Within Each User Story

- T006 before T007, T008, T009, and T010. T011 runs only those new tests.
- T012 fails before T013 changes ports. T014 implements get/find before T015 changes `enroll`. T015 runs the enrollment files, not the full suite.
- T016 records a natural pass or failure. T017 edits `enroll_student.py` only when that record is a failure.
- T018 follows T017 because both edit `tests/unit/test_enroll_student.py`. T019 and T020 can be written beside T018 after T015. T020 before T021. T018 before T022. T022 before T023. T019 before T023.
- T025 before T026. T026 before T027.
- Refactor (T028) runs after T027, and the suite must pass before and after it.

### Parallel Opportunities

- T002, T003, T004, and T005 can run together.
- T007, T008, T009, and T010 can run together after T006.
- T019 and T020 can run together after T015. T018 follows T017, then can run beside T019 and T020 because the three tests use different files.
- T013, T014, and T015 stay sequential. They share the migration and must not be treated as a green suite in the middle.

---

## Parallel Example: User Story 1

```bash
# After T015, write the new failing tests that use different files:
Task: "T019 HTTP 500 test in tests/integration/test_http_enrollment.py"
Task: "T020 rollback test in tests/integration/test_persisted_records.py"

# T018 follows T017 in tests/unit/test_enroll_student.py.
# T016 is characterization: record its natural result before T017.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2. Stop at the factory files in T011. Do not require a full-suite pass there.
2. Complete the get/find migration in order: T012, T013, T014, T015. Adapters and `enroll` are compatible before any later green claim.
3. Record the FR-014 combination run, then complete the integrity Red and Green tasks.
4. Stop after T024 and validate enrollment with those files. Browse may still fail until T026. Leave those tests in place.

### Incremental Delivery

1. Factory tests pass while the older invalid-entity tests are still waiting for their named migration tasks.
2. User Story 1 makes get/find, `enroll`, refusal evidence, persistence recovery, and the HTTP map agree.
3. User Story 2 switches `list_all` together with the course repository, browse, and HTTP, and T027 is the first full-suite pass after T001.
4. Phase 5 refactors, then measures a warning-free report, then checks boundaries, concurrency, and curl.

### Parallel Team Strategy

1. One pass through T001 and T006.
2. Split T007 through T010 across the four entity files.
3. Keep T013, T014, and T015 with one owner so the port change is not checkpointed before the adapters and `enroll` match it.
4. After T015, one person can write T019 and T020 while another finishes T016 through T018.
5. User Story 2 waits for T014 before changing `list_all` in the course repository.

---

## Notes

- [P] tasks use different files and do not depend on an unfinished task.
- Do not delete, weaken, skip, or exclude a test to reach a green run or a coverage number.
- Do not add a linter, a type checker, a dependency, or a documentation file.
- Exact business sentences stay those in `specs/001-student-self-enrollment/spec.md`. The integrity sentence stays the contract sentence and is not added to the specification.
- Existing tests that assert `course_code` order stay, even though the specification does not require that order.
- A passing characterization run is recorded and left in place. It is not converted into a failure.
- Coverage uses the trusted report from T029. New or modified business branches and the overall package total are judged separately in T030. The measurement warning has to be gone before either number is used.
