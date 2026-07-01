"""Shared pytest setup for the project tests.

I added this file for the testing task so tests can reuse the same
temporary database and sample data.
"""
import pytest

from modules.database import LibraryDatabase


@pytest.fixture()
def test_db(tmp_path):
    """Create a temporary database so tests do not modify the real library.db."""
    return LibraryDatabase(str(tmp_path / "test_library.db"))


@pytest.fixture()
def sample_book_data():
    return {
        "book_code": "BKTEST",
        "title": "Test Book",
        "author": "Test Author",
        "category": "Testing",
        "publisher": "Test Publisher",
        "isbn": "12345678910",
        "quantity": "2",
        "shelf_location": "A1",
    }


@pytest.fixture()
def sample_member_data():
    return {
        "member_code": "MBTEST",
        "name": "Test Member",
        "email": "member@example.com",
        "phone": "12345678910",
        "address": "Test Address",
    }


@pytest.fixture()
def sample_student_data():
    return {
        "student_code": "STTEST",
        "full_name": "Test Student",
        "class_name": "Software Engineering",
        "section": "a",
        "roll_no": "a",
        "email": "student@example.com",
        "phone": "12345678910",
        "address": "Student Address",
    }
