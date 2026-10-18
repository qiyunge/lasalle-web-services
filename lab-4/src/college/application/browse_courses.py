"""Browse use case. Lists every existing course; the programme does not filter it."""

from college.application.ports import CourseList, CoursePort


def browse(courses: CoursePort) -> CourseList:
    batch = courses.list_all()
    shown = tuple(sorted(batch.courses, key=lambda course: course.course_code))
    return CourseList(shown, batch.invalid)
