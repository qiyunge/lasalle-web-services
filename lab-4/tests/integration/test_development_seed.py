"""The manual HTTP check in quickstart.md starts from this seed."""

from college.app import create_app, seed_development


def test_development_seed_supports_the_manual_check(tmp_path):
    path = str(tmp_path / "college.sqlite")
    seed_development(path)
    seed_development(path)
    client = create_app(path).test_client()
    listed = client.get("/courses").get_json()["courses"]
    assert [course["course_code"] for course in listed] == ["CS101", "CS102"]
    enrolled = client.post(
        "/inscriptions", json={"acting_student_id": 1, "course_id": 1}
    )
    assert enrolled.status_code == 201
