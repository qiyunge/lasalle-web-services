# Feature Specification: Student Self-Enrollment

**Feature Branch**: `001-student-self-enrollment`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "First slice of the college management web service: a student browses available courses and enrolls in a course without administrative intervention. The enrollment belongs to the acting student. A student must not enroll another student or assign or modify grades. Clarified 2026-10-14: every existing course is available for browsing and self-enrollment, regardless of the student's programme. Enrollment periods, course capacity, prerequisites, and course availability statuses are out of scope. A student cannot enroll in a nonexistent course. Duplicate enrollment remains prohibited."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enroll in a course (Priority: P1)

A registered student chooses an existing course and enrolls in it directly. No administrator has to approve or complete the enrollment. The inscription belongs to that student and that course, and it has no grade.

**Why this priority**: Self-enrollment is the outcome of this slice. Browsing only has value because the student can act on a course without waiting for staff.

**Independent Test**: With one registered student and one existing course, the student enrolls and receives confirmation. The new inscription names that student and that course and has no grade.

**Acceptance Scenarios**:

1. **Given** a registered student and an existing course the student is not enrolled in, **When** the student enrolls in that course, **Then** an inscription is created for that student and that course, the inscription has no grade, and the student is told "You are enrolled in this course."
2. **Given** a registered student whose programme is unrelated to the course, **When** the student enrolls in an existing course, **Then** the inscription is still created. The student's programme does not block enrollment.
3. **Given** a registered student already enrolled in a course, **When** the student enrolls in a different existing course, **Then** a separate inscription is created for the second course, and the first inscription is unchanged.
4. **Given** a registered student, **When** the student enrolls in a course, **Then** no administrator action is required before the inscription exists.
5. **Given** a registered student and an existing course, **When** the student enrolls, **Then** the enrollment is not refused for an enrollment period, a full course, a missing prerequisite, a course availability status, or a mismatch with the student's programme.

---

### User Story 2 - Browse available courses (Priority: P2)

A registered student reviews the courses the college offers so they can choose one to enroll in. Every existing course is shown, including courses outside the student's programme and courses the student is already enrolled in.

**Why this priority**: The student needs the college course list in order to choose an enrollment. The list is useful on its own even before an enrollment is submitted.

**Independent Test**: With several existing courses, the student opens the course list and sees each of those courses, and does not see courses that do not exist.

**Acceptance Scenarios**:

1. **Given** one or more existing courses, **When** a registered student browses courses, **Then** every existing course is shown.
2. **Given** a course that is not part of the student's programme, **When** the student browses courses, **Then** that course is still shown.
3. **Given** a course the student is already enrolled in, **When** the student browses courses, **Then** that course is still shown.
4. **Given** no existing courses, **When** a registered student browses courses, **Then** the student sees an empty course list.

---

### Edge Cases

- A student enrolls in a course that does not exist. The enrollment fails and no inscription is created. The student is told "That course does not exist."
- A student enrolls again in a course they are already enrolled in. The enrollment fails and no second inscription is created. The existing inscription is unchanged, including its grade if a grade was already present. The student is told "You are already enrolled in this course."
- The person attempting enrollment is not a registered student. The enrollment fails and no inscription is created. They are told "Only a registered student can enroll in a course."
- A student tries to create or change an enrollment for a different student. Nothing is created or changed for the other student. The acting student is told "You can only enroll yourself."
- A student tries to assign, change, or remove a grade, including a grade on their own enrollment. No grade is assigned, changed, or removed. The student is told "Students cannot assign, change, or remove a grade."
- A failed enrollment leaves every existing inscription unchanged.
- Two students enroll in the same course. Both enrollments succeed. The unique-enrollment rule applies to one student and one course, not to the course as a whole.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A registered student can browse every course the college offers.
- **FR-002**: Browsing includes each existing course regardless of the student's programme and regardless of whether the student is already enrolled in it.
- **FR-003**: A registered student can enroll in an existing course without an administrator approving or completing the enrollment.
- **FR-004**: A successful enrollment creates one inscription for the acting student and the chosen course, and that inscription has no grade.
- **FR-005**: On success, the student is told "You are enrolled in this course."
- **FR-006**: Enrollment in a course that does not exist fails, creates no inscription, and tells the student "That course does not exist."
- **FR-007**: A student cannot enroll in the same course more than once. A duplicate enrollment fails, creates no additional inscription, leaves the existing inscription unchanged, and tells the student "You are already enrolled in this course."
- **FR-008**: A person who is not a registered student cannot enroll. The attempt fails, creates no inscription, and tells them "Only a registered student can enroll in a course."
- **FR-009**: A student cannot create or modify an enrollment for another student. The attempt changes nothing and tells the acting student "You can only enroll yourself."
- **FR-010**: A student cannot assign, change, or remove a grade, including a grade on their own enrollment. The attempt changes no grade and tells the student "Students cannot assign, change, or remove a grade."
- **FR-011**: This feature does not reject an enrollment because of an enrollment period, a course capacity limit, a prerequisite, a course availability status, or the student's programme.
- **FR-012**: A failed enrollment does not change existing inscriptions.

### Key Entities *(include if feature involves data)*

- **Student**: A learner registered in a programme. The acting student is the student performing the browse or enrollment. This feature does not register students or change programme membership.
- **Course**: A course offered by the college. Every existing course can be browsed and is eligible for self-enrollment, subject only to the rules in this specification.
- **Inscription**: One student's enrollment in one course. A student self-enrollment creates an inscription for the acting student only, with no grade.
- **Note**: The grade associated with an inscription. This feature does not create, change, or remove a note.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A registered student can browse the college courses and enroll in an existing course in under 3 minutes, without an administrator taking part.
- **SC-002**: In a review of the course list, 100% of existing courses are visible to the student, including courses outside that student's programme.
- **SC-003**: 100% of successful enrollments belong to the acting student, name the chosen course, and have no grade.
- **SC-004**: 100% of attempts to enroll in a missing course, to enroll twice in the same course, or to enroll when the person is not a registered student leave existing inscriptions unchanged and show the specified message.
- **SC-005**: Across the acceptance scenarios, a student has no successful outcome that enrolls another student or that assigns, changes, or removes a grade.

## Out of Scope

- Creating or maintaining programmes, students, or courses.
- How the acting student is recognized. This feature starts from a known acting student and does not define that recognition.
- Enrollment periods, course capacity limits, prerequisites, and course availability statuses.
- Limiting browse or enrollment results by the student's programme.
- Showing the student's existing inscriptions, or marking a browsed course as already enrolled. A duplicate enrollment is reported only when the student tries to enroll again.
- Withdrawing from a course, or otherwise changing or removing an existing inscription.
- Assigning, changing, removing, or displaying grades. Grade management remains reserved for authorized college staff.
- An administrator enrolling a student, approving an enrollment, or acting on behalf of a student.
- Any enrollment business rule not already stated in this specification or in the project constitution.

## Assumptions

- Programmes, registered students, and courses already exist before a student uses this feature.
- Every registered student already belongs to a programme. That membership does not decide which courses the student may browse or join.
- The acting student is already known when browsing or enrolling begins. Establishing that identity is outside this feature.
- A course does not need to be linked to a programme to be browsed or enrolled in.
- An inscription created here has no grade. This feature does not define a permitted grade range, because it never assigns a grade.
- A grade that staff have already recorded on an existing inscription is left as it is when a duplicate enrollment is refused.
- The quoted sentences in this specification are the exact user-facing messages for the named outcomes.
