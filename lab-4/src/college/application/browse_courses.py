"""Browse use case. Reaches the course capability through its port only."""

from college.application.ports import CourseList


def browse(courses) -> CourseList:
    batch = courses.list_all()
    shown = tuple(sorted(batch.courses, key=lambda course: course.course_code))
    return CourseList(shown, tuple(batch.invalid))
