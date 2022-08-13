import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student
from django_testing import settings


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_create_course(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get(f'/api/v1/courses/{course[0].id}/')
    assert response.status_code == 200
    assert course[0].id == response.data['id']


@pytest.mark.django_db
def test_list_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    assert len(courses) == len(response.data)
    for i, course in enumerate(response.data):
        assert course['id'] == courses[i].id


@pytest.mark.django_db
def test_filter_id_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'/api/v1/courses/?id={courses[1].id}')
    assert response.status_code == 200
    assert courses[1].id == response.data[0]['id']


@pytest.mark.django_db
def test_filter_name_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'/api/v1/courses/?name={courses[2].name}')
    assert response.status_code == 200
    assert courses[2].name == response.data[0]['name']


@pytest.mark.django_db
def test_filter_name_courses(client):
    response = client.post('/api/v1/courses/', data={'name': 'Test Course'})
    assert response.status_code == 201
    assert response.data['id'] == Course.objects.first().id


@pytest.mark.django_db
def test_update_courses(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.patch(f'/api/v1/courses/{course[0].id}/', data={'name': 'Test Course Update'})
    assert response.status_code == 200
    assert response.data['name'] == Course.objects.first().name


@pytest.mark.django_db
def test_delete_courses(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.delete(f'/api/v1/courses/{course[0].id}/')
    assert response.status_code == 204
    assert course[0] != Course.objects.filter(id=course[0].id)


@pytest.mark.django_db
def test_max_students_per_course_positive(client, student_factory):
    students = student_factory(_quantity=20)
    students_ids = [student.id for student in students]
    response = client.post('/api/v1/courses/',
                           data={'name': 'Test Course', 'students': students_ids})
    assert response.status_code == 201


@pytest.mark.django_db
def test_max_students_per_course_negative(client, student_factory):
    students = student_factory(_quantity=21)
    students_ids = [student.id for student in students]

    with pytest.raises(ValidationError):
        response = client.post('/api/v1/courses/',
                               data={'name': 'Test Course', 'students': students_ids})