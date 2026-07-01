"""Regression tests for behavior that should not break later."""
import pytest


def test_duplicate_student_roll_number_is_rejected(test_db, sample_student_data):
    test_db.add_student(sample_student_data)

    duplicate = sample_student_data.copy()
    duplicate["student_code"] = "STTEST2"
    duplicate["email"] = "student2@example.com"
    duplicate["phone"] = "12345678910"

    with pytest.raises(ValueError, match="same code, roll number, email, or phone"):
        test_db.add_student(duplicate)


def test_same_book_cannot_be_issued_twice_to_same_member(
    test_db,
    sample_book_data,
    sample_member_data,
):
    book_id = test_db.add_book(sample_book_data)
    member_id = test_db.add_member(sample_member_data)

    test_db.issue_book(book_id, member_id, issue_date="2026-01-01")

    with pytest.raises(ValueError, match="already issued"):
        test_db.issue_book(book_id, member_id, issue_date="2026-01-02")

    book = test_db.get_book_by_id(book_id)
    assert book["available_quantity"] == 1
