# Tasks: Student Self-Enrollment

**Input**: Design documents from `/specs/001-student-self-enrollment/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/student-self-enrollment.md, quickstart.md, constitution 1.4.0

**Tests**: Required by constitution Principles XVI–XX. Acceptance tests are derived from the specification scenarios and are ordered before the implementation they verify. The runner is pytest, as required by Principle XVII and recorded in plan.md.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Paths are relative to `lab-4/`. Source lives under `src/college/`. Tests live under `tests/`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and pytest branch-coverage configuration

- [x] T001 Create `pyproject.toml` requiring Python >=3.12, runtime dependency Flask==3.1.3, and a `dev` extra with pytest and pytest-cov. Point package discovery at `src/`. Set pytest `addopts` to `--cov=college --cov-branch --cov-fail-under=100` and omit `tests/` from coverage.
- [x] T002 [P] Create empty package files `src/college/__init__.py`, `src/college/domain/__init__.py`, `src/college/application/__init__.py`, `src/college/adapters/__init__.py`, `src/college/adapters/inbound/__init__.py`, `src/college/adapters/outbound/__init__.py`, `tests/unit/__init__.py`, and `tests/integration/__init__.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wiring boundaries that every story uses, with no enrollment or browse rules

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create port interfaces only in `src/college/application/ports.py`. Declare the operations a use case needs. Do not import Flask, `sqlite3`, or an adapter, and do not decide a business outcome.
- [x] T004 Create the composition root in `src/college/app.py` so it can build a Flask app and is the only production module that will construct adapters. Do not enroll a student or filter courses in this task.
- [x] T005 [P] Create the transaction boundary in `src/college/adapters/outbound/sqlite_unit_of_work.py` using `sqlite3`. It opens a connection and rolls back on failure. It does not choose an enrollment outcome or a response sentence.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Enroll in a course (Priority: P1) 🎯 MVP

**Goal**: A registered student enrolls in an existing course without an administrator. The inscription belongs to that student and course and has no grade.

**Independent Test**: With one registered student and one existing course, the student enrolls and receives confirmation. The new inscription names that student and that course and has no grade.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, run them, and observe them fail for the expected reason before Phase 3 implementation**

- [x] T006 [P] [US1] Write failing pytest acceptance tests in `tests/unit/test_enroll_student.py` for spec acceptance scenarios 1–5 and the enrollment edge cases. Assert the exact sentences "You are enrolled in this course.", "That course does not exist.", "You are already enrolled in this course.", "Only a registered student can enroll in a course.", "You can only enroll yourself.", and "Students cannot assign, change, or remove a grade." A duplicate leaves an existing note unchanged. A failed enrollment leaves every inscription unchanged. Two students may enroll in the same course. Programme mismatch does not refuse enrollment. Run pytest on this file and record that it fails because the enrollment use case is absent.
- [x] T007 [P] [US1] Write failing pytest HTTP tests in `tests/integration/test_http_enrollment.py` for `POST /inscriptions` in `contracts/student-self-enrollment.md`, including 201, 400, 404, and 409 bodies. Run pytest on this file and record that it fails because the route is absent.
- [x] T008 [P] [US1] Write a failing pytest integration test in `tests/integration/test_inscription_concurrency.py`: two concurrent enrollments for the same student and course leave one inscription, leave its note unchanged, and return the already-enrolled outcome for the conflicting attempt. Run pytest on this file and record that it fails because persistence conflict handling is absent.

### Implementation for User Story 1

- [x] T009 [P] [US1] Create the programme type in `src/college/domain/programme.py`. Quote the data-model constraint: id is required, "Identifier." Do not import Flask, `sqlite3`, or another capability's domain module.
- [x] T010 [P] [US1] Create the student type in `src/college/domain/student.py`. Quote: id required "Identifier."; name required "Must be present."; email required "Must be present. Unique among students."; programme_id required "Must reference an existing programme." "A text value is present when it is a non-empty string. Uniqueness compares the stored value exactly." Do not import the course or inscription domain modules.
- [x] T011 [P] [US1] Create the course type in `src/college/domain/course.py`. Quote: id required "Identifier. The inscription references this identifier."; course_code required "Must be present. Unique among courses."; name required "Must be present. Not required to be unique."
- [x] T012 [P] [US1] Create the inscription type in `src/college/domain/inscription.py`. Quote: id required "Identifier. Assigned when the inscription is created."; student_id required "Must reference an existing registered student. On self-enrollment this is the acting student."; course_id required "Must reference an existing course."; note not required "Absent when this slice creates the inscription. This slice never writes a note." Uniqueness is "at most one inscription for a given `(student_id, course_id)`."
- [x] T013 [P] [US1] Implement `src/college/adapters/outbound/sqlite_programme_repository.py` so it reads and writes programme data only.
- [x] T014 [P] [US1] Implement `src/college/adapters/outbound/sqlite_student_repository.py` so it reads and writes student data only.
- [x] T015 [P] [US1] Implement `src/college/adapters/outbound/sqlite_course_repository.py` so it reads and writes course data only.
- [x] T016 [P] [US1] Implement `src/college/adapters/outbound/sqlite_inscription_repository.py` so it reads and writes inscription data only. On a concurrent duplicate it exposes a persistence conflict and does not decide the business outcome or the response wording.
- [x] T017 [US1] Implement `src/college/application/enroll_student.py` so the use case owns eligibility, existence, and business success. Apply this refusal order and stop at the first match: missing or non-integer `acting_student_id` or `course_id`; `note` present; `student_id` present and different from `acting_student_id`; student missing, name missing, email missing, or programme missing; course missing, course code missing, or course name missing; inscription already exists for that student and course. Map a persistence conflict to the already-enrolled outcome. Reach other capabilities only through ports. Do not import Flask or `sqlite3`.
- [x] T018 [US1] Implement `POST /inscriptions` in `src/college/adapters/inbound/http.py`. Parse and validate request structure, build the enrollment command, call the use case, and map its outcome to the contract status and body. Preserve the exact spec sentences. Do not decide eligibility, existence, or business success.
- [x] T019 [US1] Bind the enrollment use case and its adapters only in `src/college/app.py`.
- [x] T020 [US1] Re-run pytest on `tests/unit/test_enroll_student.py`, `tests/integration/test_http_enrollment.py`, and `tests/integration/test_inscription_concurrency.py`. Confirm they pass. Refactor `src/college/application/enroll_student.py` and `src/college/adapters/inbound/http.py` only while those tests stay green.

**Checkpoint**: User Story 1 is independently functional and its tests pass

---

## Phase 4: User Story 2 - Browse available courses (Priority: P2)

**Goal**: A registered student sees every existing course, including courses outside the student's programme and courses the student is already enrolled in.

**Depends on**: T011, which creates the course type in `src/college/domain/course.py`. Do not start User Story 2 before T011 is complete.

**Independent Test**: With several existing courses, the student opens the course list and sees each of those courses, and does not see courses that do not exist.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, run them, and observe them fail for the expected reason before Phase 4 implementation**

- [x] T021 [P] [US2] Write failing pytest acceptance tests in `tests/unit/test_browse_courses.py` for spec acceptance scenarios 1–4. The list includes every course, a course outside the student's programme, and a course already enrolled. No courses yields an empty list. Each course has id, course_code, and name. Order is course_code ascending. Two courses may share a name when their codes differ. Run pytest on this file and record that it fails because the browse use case is absent.
- [x] T022 [P] [US2] Write failing pytest HTTP tests in `tests/integration/test_http_courses.py` for `GET /courses` in `contracts/student-self-enrollment.md`, including `200` with `"courses": []`. Run pytest on this file and record that it fails because the route is absent.

### Implementation for User Story 2

- [x] T023 [US2] Implement `src/college/application/browse_courses.py` so it returns every valid course through the course port only. Do not filter by programme or by an existing inscription, and do not call `enroll_student`.
- [x] T024 [US2] Implement `GET /courses` in `src/college/adapters/inbound/http.py`. Call the browse use case and map its list to the contract body. Do not apply a business filter in the route.
- [x] T025 [US2] Bind the browse use case in `src/college/app.py` without moving adapter construction out of the composition root.
- [x] T026 [US2] Re-run pytest on `tests/unit/test_browse_courses.py` and `tests/integration/test_http_courses.py`. Confirm they pass. Refactor `src/college/application/browse_courses.py` only while those tests stay green.

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Recorded completion evidence required by constitution Principles XVIII–XX

- [x] T027 [P] Run pytest with branch coverage from `lab-4/` and write the output to `specs/001-student-self-enrollment/evidence/coverage.txt`. Completion of this task requires 100% branch coverage of project-owned executable application code. Line coverage is informational. Coverage excludes third-party dependencies, test code, and generated code. Document any further exclusion in that evidence file with a justification.
- [x] T028 [P] Start the app from `src/college/app.py` and run the reproducible curl checks in `quickstart.md` plus the failure outcomes in `contracts/student-self-enrollment.md`. Write the commands and responses to `specs/001-student-self-enrollment/evidence/curl.txt`. The evidence must include "You are enrolled in this course.", "That course does not exist.", "You are already enrolled in this course.", "Only a registered student can enroll in a course.", "You can only enroll yourself.", and "Students cannot assign, change, or remove a grade."

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories proceed in priority order (P1 → P2) so each story's tests fail before its implementation
  - US2 also depends on T011 and must stay independently testable
- **Polish (Phase 5)**: Depends on the user stories selected for completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependency on User Story 2
- **User Story 2 (P2)**: Depends on Foundational (Phase 2) and on T011. The browse tests and use case do not require an enrollment route.

### Within Each User Story

- Tests MUST be written and FAIL for the expected reason before implementation
- Domain types before repositories
- Repositories and the use case before the HTTP adapter
- Use case before the composition-root binding
- Green tests before refactor

### Parallel Opportunities

- T001 and T002 can run in parallel
- T003 and T005 can run in parallel; T004 follows T003
- T006, T007, and T008 can run in parallel
- T009, T010, T011, and T012 can run in parallel after the US1 tests exist
- T013, T014, T015, and T016 can run in parallel after the domain types they persist exist
- T021 and T022 can run in parallel after T011
- T027 and T028 can run in parallel after the implemented stories are green

---

## Parallel Example: User Story 1

```bash
# Write the failing US1 tests together:
Task: "Write failing pytest acceptance tests in tests/unit/test_enroll_student.py"
Task: "Write failing pytest HTTP tests in tests/integration/test_http_enrollment.py"
Task: "Write a failing pytest integration test in tests/integration/test_inscription_concurrency.py"

# Then create the domain types together:
Task: "Create the programme type in src/college/domain/programme.py"
Task: "Create the student type in src/college/domain/student.py"
Task: "Create the course type in src/college/domain/course.py"
Task: "Create the inscription type in src/college/domain/inscription.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1, tests first
4. **STOP and VALIDATE**: User Story 1 tests pass
5. Demo enrollment before starting browse

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → enrollment tests green → MVP
3. User Story 2 → browse tests green
4. Phase 5 → recorded branch-coverage and curl evidence before any completion claim

### Parallel Team Strategy

With multiple developers:

1. Complete Setup and Foundational together
2. After that:
   - Developer A: User Story 1 tests, then enrollment implementation through T011
   - Developer B: User Story 2 tests, then browse implementation, only after T011 is complete
3. Do not claim the feature complete until T027 and T028 evidence exists

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps the task to a user story
- Each user story is independently completable and testable
- Verify tests fail for the expected reason before implementing
- A green automated test run is not feature completion
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
- Avoid vague tasks, same-file conflicts, and cross-story dependencies that break independence
