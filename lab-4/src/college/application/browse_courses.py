"""Browse use case. Reaches the course capability through its port only."""


def browse(courses) -> list:
    shown = [course for course in courses.list_all() if course.is_complete()]
    return sorted(shown, key=lambda course: course.course_code)
