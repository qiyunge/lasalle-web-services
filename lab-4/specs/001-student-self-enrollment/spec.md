# Feature Specification: Student Self-Enrollment

**Feature Branch**: `001-student-self-enrollment`

**Created**: 2026-10-14

**Updated**: 2026-10-16

**Status**: Draft

**Input**: User description: "Align the existing Student Self-Enrollment specification with the current constitution. This is not a new feature. The existing specification remains the source of this feature's business rules. The constitution does not adopt those rules. Accepted behavior is unchanged: a student browses available courses and enrolls without administrative intervention. The enrollment belongs to the acting student supplied by a trusted caller context. The enrollment request does not accept a target student. A student must not assign, change, or remove a grade. Every existing course is available for browsing and self-enrollment, regardless of the student's programme. Enrollment periods, course capacity, prerequisites, and course availability statuses are out of scope. A student cannot enroll in a nonexistent course. Duplicate enrollment remains prohibited."

## Audience

Registered students. A registered student browses courses and enrolls. College staff are not actors in this feature. Only authorized staff may assign, change, or remove a grade, and this feature does not give anyone that action.

## Clarifications

### Session 2026-10-15

- Q: When one enrollment attempt breaks more than one business rule, which refusal should the student see? → A: After input validation has produced no errors, stop at the first business refusal: a grade attempt; then the acting student is not registered; then the course does not exist; then the student is already enrolled. The earlier "enrolling someone else" step was removed on 2026-10-16.

### Session 2026-10-16

- Q: Does principle A10 replace that first-match rule? → A: No. A10 accumulates independent input-validation failures. Those failures are resolved before any business refusal is evaluated. When any input-validation error is present, the result is that validation outcome alone. Business refusals stay in this specification and are not accumulated. FR-014 remains the first-match rule for those refusals. RF-001 is resolved.
- Q: Who is the student on a successful enrollment, and may the request name someone else? → A: A trusted caller context supplies the acting student's identity. Successful enrollment always creates the inscription for that acting student. The enrollment request does not accept `student_id` or any other target-student field. A supplied target-student field is an input-validation error, including when its value equals the acting student's identifier. It is not a business refusal, and this feature does not use "You can only enroll yourself." An acting student who is not registered receives "Only a registered student can enroll in a course." Recognizing and authenticating the acting student, and establishing the trusted caller context, remain outside this feature.
- Q: What is the contract error for a target-student field? → A: Each supplied target-student field, including `student_id`, is an input-validation error with code `target_student_not_accepted` and that field's name. It accumulates with every other independent input-validation error on the same request. This feature does not define an authentication mechanism for that error.
- Q: When is a note a grade attempt? → A: A present `note` field is a grade attempt, including null, an empty string, or any other supplied value. An omitted `note` field is not a grade attempt. The refusal message remains "Students cannot assign, change, or remove a grade."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enroll in a course (Priority: P1)

A registered student chooses an existing course and enrolls in it directly. No administrator has to approve or complete the enrollment. The inscription belongs to that student and that course, and it has no grade.

**Why this priority**: Self-enrollment is the outcome of this slice. Browsing only has value because the student can act on a course without waiting for staff.

**Independent Test**: With one registered student and one existing course, the student enrolls and receives confirmation. The new inscription names that student and that course and has no grade.

**Acceptance Scenarios**:

1. **Given** a registered acting student and an existing course that student is not enrolled in, **When** the student enrolls in that course without a target-student field and without a `note` field, **Then** an inscription is created for that acting student and that course, the inscription has no grade, and the student is told "You are enrolled in this course."
2. **Given** a registered student whose programme is unrelated to the course, **When** the student enrolls in an existing course, **Then** the inscription is still created. The student's programme does not block enrollment.
3. **Given** a registered student already enrolled in a course, **When** the student enrolls in a different existing course, **Then** a separate inscription is created for the second course, and the first inscription is unchanged.
4. **Given** a registered student, **When** the student enrolls in a course, **Then** no administrator action is required before the inscription exists.
5. **Given** a registered student and an existing course, **When** the student enrolls, **Then** the enrollment is not refused for an enrollment period, a full course, a missing prerequisite, a course availability status, or a mismatch with the student's programme.
6. **Given** two registered students and one existing course, **When** each student enrolls in that course, **Then** both enrollments succeed. One inscription exists for each student.

---

### User Story 2 - Browse available courses (Priority: P2)

A registered student reviews the courses the college offers so they can choose one to enroll in. Every existing course is shown, including courses outside the student's programme and courses the student is already enrolled in. Two courses may share a name. Each shown course can be told apart by its identifier and its course code.

**Why this priority**: The student needs the college course list in order to choose an enrollment. The list is useful on its own even before an enrollment is submitted.

**Independent Test**: With several existing courses, the student opens the course list and sees each of those courses, and does not see a course that does not exist or that lacks a nonempty course code or a nonempty name.

**Acceptance Scenarios**:

1. **Given** one or more existing courses, **When** a registered student browses courses, **Then** every existing course is shown, and each shown course includes its identifier, course code, and name.
2. **Given** a course that is not part of the student's programme, **When** the student browses courses, **Then** that course is still shown.
3. **Given** a course the student is already enrolled in, **When** the student browses courses, **Then** that course is still shown.
4. **Given** no existing courses, **When** a registered student browses courses, **Then** the student sees an empty course list.
5. **Given** two existing courses that share a name and have different course codes, **When** a registered student browses courses, **Then** both courses are shown.
6. **Given** a course record that has no course code or no name, **When** a registered student browses courses, **Then** that record is not shown.

---

### Edge Cases

- A student enrolls in a course that does not exist, or in a course record that has no course code or no name. The enrollment fails and no inscription is created. The student is told "That course does not exist."
- A student enrolls again in a course they are already enrolled in. The enrollment fails and no second inscription is created. The existing inscription is unchanged, including its grade if a grade was already present. The student is told "You are already enrolled in this course."
- Two enrollment attempts for the same student and the same course overlap. Exactly one inscription remains. The attempt that does not create it fails with "You are already enrolled in this course." An existing grade on that inscription is unchanged.
- The person attempting enrollment is not a registered student. That includes no student record, a student with no name, a student with no email address, a student whose programme does not exist, and a student whose programme record has no nonempty name. The enrollment fails and no inscription is created. They are told "Only a registered student can enroll in a course."
- The enrollment request includes `student_id` or any other target-student field, even when the value equals the acting student's identifier. Nothing is written. The result is an input-validation error with code `target_student_not_accepted` and that field's name. It is not a business refusal. Other independent input-validation errors on the same request are accumulated with it. No business sentence is shown.
- A student tries to assign, change, or remove a grade, including a grade on their own enrollment. A present `note` field is that attempt, including null, an empty string, or any other supplied value. An omitted `note` field is not that attempt. No grade is assigned, changed, or removed. The student is told "Students cannot assign, change, or remove a grade."
- A failed enrollment leaves every existing inscription unchanged.
- Two students enroll in the same course. Both enrollments succeed. The one-enrollment rule applies to one student and one course, not to the course as a whole.
- One enrollment attempt violates more than one business refusal, and input validation has produced no errors. The attempt fails and changes nothing. The student is told the message for the first matching rule: a grade attempt; then the acting student is not a registered student; then the course does not exist; then the student is already enrolled. A grade attempt by an unregistered student is told "Students cannot assign, change, or remove a grade."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A registered student can browse every existing course the college offers.
- **FR-002**: Browsing includes each existing course regardless of the student's programme and regardless of whether the student is already enrolled in it. A course that lacks a nonempty course code or a nonempty name is not an existing course and is not shown.
- **FR-003**: Each course shown to the student includes its identifier, its course code, and its name. Course codes are unique. Course names may be shared by more than one course.
- **FR-004**: A registered student can enroll in an existing course without an administrator approving or completing the enrollment.
- **FR-005**: A successful enrollment creates one inscription for the acting student and the chosen course, and that inscription has no grade. The student on that inscription is always the acting student supplied by the trusted caller context.
- **FR-006**: On success, the student is told "You are enrolled in this course."
- **FR-007**: Enrollment in a course that does not exist fails, creates no inscription, and tells the student "That course does not exist." A course record with no course code or no name does not exist for this purpose.
- **FR-008**: A student cannot enroll in the same course more than once, including when two attempts for that student and course overlap. A duplicate enrollment fails, creates no additional inscription, leaves the existing inscription and any grade already on it unchanged, and tells the student "You are already enrolled in this course."
- **FR-009**: A person who is not a registered student cannot enroll. A registered student has an identifier, a nonempty name, a nonempty email address, and a reference to an existing programme. An existing programme has an identifier and a nonempty name. A programme record that lacks either is not an existing programme. Student email addresses are unique. An attempt by anyone who does not meet that definition fails, creates no inscription, and tells them "Only a registered student can enroll in a course."
- **FR-010**: Successful enrollment creates the inscription for the acting student supplied by the trusted caller context. The enrollment request does not accept `student_id` or any other target-student field. A supplied target-student field is an input-validation error with code `target_student_not_accepted` and that field's name, including when its value equals the acting student's identifier. It is not a business refusal. Independent input-validation errors on the same request are accumulated. Input validation completes before FR-014. When any input-validation error is present, the result is that validation outcome alone, nothing is written, and no business sentence is shown. Enrollment on behalf of another student is not supported. This feature does not define an authentication mechanism.
- **FR-011**: A student cannot assign, change, or remove a grade, including a grade on their own enrollment. A present `note` field is a grade attempt, including null, an empty string, or any other supplied value. An omitted `note` field is not a grade attempt. The attempt changes no grade and tells the student "Students cannot assign, change, or remove a grade."
- **FR-012**: This feature does not reject an enrollment because of an enrollment period, a course capacity limit, a prerequisite, a course availability status, or the student's programme.
- **FR-013**: A failed enrollment does not change existing inscriptions.
- **FR-014**: When input validation has produced no errors and one enrollment attempt violates more than one business refusal, the attempt fails, changes nothing, and shows the message for the first matching rule only. The order is: a grade attempt ("Students cannot assign, change, or remove a grade."); then the acting student is not a registered student ("Only a registered student can enroll in a course."); then the course does not exist ("That course does not exist."); then the student is already enrolled ("You are already enrolled in this course.").

### Key Entities *(include if feature involves data)*

- **Programme**: An academic programme offered by the college. A programme has an identifier and a nonempty name. A programme record that lacks an identifier or a nonempty name is not an existing programme. A registered student belongs to one existing programme. This feature does not create or change programmes, and a programme does not decide which courses can be browsed or joined.
- **Student**: A learner registered in a programme. A registered student has an identifier, a nonempty name, a nonempty email address, and a reference to an existing programme. Email addresses are unique among students. The acting student is the student performing the browse or enrollment. This feature does not register students or change programme membership.
- **Course**: A course offered by the college. An existing course has an identifier, a nonempty course code, and a nonempty name. Course codes are unique. Course names may repeat. Every existing course can be browsed and is eligible for self-enrollment, subject only to the rules in this specification.
- **Inscription**: One student's enrollment in one course. It references an existing registered student and an existing course. A student has at most one inscription for a given course. A successful self-enrollment creates an inscription for the acting student only, with no grade. The acting student is the student supplied by the trusted caller context.
- **Note**: The optional grade associated with an inscription. A present `note` on an enrollment request is a grade attempt, including null, an empty string, or any other supplied value. An omitted `note` is not a grade attempt. This feature does not create, change, or remove a note, and it does not state a permitted grade range.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A registered student successfully enrolls in an existing course without an administrator taking part, and the inscription created by that enrollment is persisted and observable.
- **SC-002**: In a review of the course list, 100% of existing courses are visible to the student, including courses outside that student's programme and courses that share a name, and 0% of course records that lack a nonempty code or a nonempty name are visible.
- **SC-003**: 100% of successful enrollments belong to the acting student, name the chosen course, and have no grade.
- **SC-004**: 100% of attempts to enroll in a missing or incomplete course, to enroll twice in the same course, or to enroll when the person is not a registered student, including when that person's programme lacks a nonempty name, leave existing inscriptions unchanged and show the specified message.
- **SC-005**: Across the acceptance scenarios, a successful enrollment belongs to the acting student, and a student has no successful outcome that assigns, changes, or removes a grade. A request that supplies a target-student field does not create an inscription.

## Out of Scope

- Creating or maintaining programmes, students, or courses.
- How the acting student is recognized or authenticated. A trusted caller context supplies that identity. This feature does not establish or verify the context.
- A failure message for a duplicate student email. This feature does not create students. Email uniqueness remains a property of student identity.
- A permitted numerical range for a grade. This feature never assigns a grade. The feature that assigns a grade must state that range.
- Enrollment periods, course capacity limits, prerequisites, and course availability statuses.
- Limiting browse or enrollment results by the student's programme.
- The order in which courses are shown. The required outcome is the set of existing courses, not a sort order.
- Showing the student's existing inscriptions, or marking a browsed course as already enrolled. A duplicate enrollment is reported only when the student tries to enroll again.
- Withdrawing from a course, or otherwise changing or removing an existing inscription, except that a refused duplicate leaves the existing inscription unchanged.
- Assigning, changing, removing, or displaying grades. Grade management remains reserved for authorized college staff.
- An administrator enrolling a student, approving an enrollment, delegated enrollment, or acting on behalf of a student.
- Any enrollment business rule not already stated in this specification.

## Review flags

RF-001 is resolved. It does not change the accepted requirements above.

- **RF-001**: Resolved on 2026-10-16. Constitution 6.0.1 principle A10 accumulates independent input-validation failures. It does not accumulate business refusals. FR-014 stays the first-match rule for those refusals. A later approved clarification on the same date removed "You can only enroll yourself." from the business refusals. That sentence was not replaced.
- **RF-002**: No other feature specification exists in this project, so no conflict with another accepted specification was found.

## Assumptions

- Programmes, registered students, and courses already exist before a student uses this feature.
- A name, email address, course code, course name, or programme name is nonempty when it contains at least one character. This feature does not define removal of surrounding spaces.
- A programme name is not required to be unique. The identifier tells one programme from another. This feature does not define a failure for two programmes that share a name.
- The acting student is already supplied by a trusted caller context when browsing or enrolling begins. This feature does not authenticate that student or define how the context was established.
- A supplied `student_id` or other target-student field is an input-validation error with code `target_student_not_accepted`. It is not a business refusal. Independent input-validation errors on one request are accumulated, and that validation finishes before FR-014.
- A present `note` field is a grade attempt, including null, an empty string, or any other supplied value. An omitted `note` field is not a grade attempt.
- A course does not need to be linked to a programme to be browsed or enrolled in.
- An inscription created here has no grade.
- A grade that staff have already recorded on an existing inscription is left as it is when a duplicate enrollment is refused.
- The quoted sentences in this specification are the exact user-facing messages for the named outcomes. When one attempt breaks more than one rule, FR-014 chooses the one message.
- This specification is the source of the business rules for student self-enrollment. The constitution does not adopt those rules. Rules already stated here remain in force.
- How a refusal is carried or checked inside the service is not a business rule. This specification states the messages and when each message applies.
- Student email uniqueness compares students as the college stores them. This feature does not define a new comparison rule and does not repair existing duplicate emails.
