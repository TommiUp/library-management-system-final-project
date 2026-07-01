from modules.database import LibraryDatabase


def test_password_hash_and_verify():
    password_hash = LibraryDatabase.hash_password("secret123")

    assert password_hash != "secret123"
    assert LibraryDatabase.verify_password("secret123", password_hash)
    assert not LibraryDatabase.verify_password("wrong-password", password_hash)


def test_calculate_fine_returns_zero_before_due_date():
    fine = LibraryDatabase.calculate_fine("2026-01-10", "2026-01-09")

    assert fine == 0.0


def test_calculate_fine_returns_amount_for_overdue_days():
    fine = LibraryDatabase.calculate_fine("2026-01-10", "2026-01-13")

    assert fine == 30.0


def test_next_code_generates_next_number():
    code = LibraryDatabase._next_code("ST", ["ST0001", "ST0002"])

    assert code == "ST0003"
