def test_student_with_linked_account_can_be_created_and_deleted(test_db, sample_student_data):
    account = {
        "username": "student",
        "password": "student123",
        "role": "student",
    }

    student_id = test_db.add_student(sample_student_data, account)

    student = test_db.get_student_by_id(student_id)
    user = test_db.authenticate_user("student", "student123")

    assert student is not None
    assert student["full_name"] == "Test Student"
    assert student["account_username"] == "student"
    assert user is not None
    assert user["role"] == "student"

    test_db.delete_student(student_id)

    assert test_db.get_student_by_id(student_id) is None
    assert test_db.get_user_by_username("student") is None


def test_issue_and_return_book_updates_availability_and_fine(
    test_db,
    sample_book_data,
    sample_member_data,
):
    book_id = test_db.add_book(sample_book_data)
    member_id = test_db.add_member(sample_member_data)

    issue_id = test_db.issue_book(book_id, member_id, issue_date="2026-01-01")

    book_after_issue = test_db.get_book_by_id(book_id)
    assert book_after_issue["available_quantity"] == 1

    fine = test_db.return_book(issue_id, return_date="2026-01-20")

    book_after_return = test_db.get_book_by_id(book_id)
    issue = test_db.fetch_issued_books()[0]

    assert fine == 50.0
    assert book_after_return["available_quantity"] == 2
    assert issue["status"] == "Returned"
    assert issue["fine_amount"] == 50.0
    