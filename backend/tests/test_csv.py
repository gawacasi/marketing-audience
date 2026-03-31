import pytest

from app.csv_service import parse_csv_content, validate_row_dict
from app.schemas import RowError


def test_validate_row_ok():
    pr, errs = validate_row_dict(
        2,
        {"id": "1", "name": "Ana", "age": "25", "city": "SP", "income": "1000"},
    )
    assert pr is not None
    assert errs == []
    assert pr.customer_id == 1
    assert pr.age == 25
    assert pr.income == 1000.0


def test_validate_row_invalid_id():
    pr, errs = validate_row_dict(
        3,
        {"id": "-1", "name": "Ana", "age": "25", "city": "SP", "income": "0"},
    )
    assert pr is None
    assert any(e.field == "id" for e in errs)


def test_validate_row_invalid_income_negative():
    pr, errs = validate_row_dict(
        4,
        {"id": "1", "name": "Ana", "age": "25", "city": "SP", "income": "-1"},
    )
    assert pr is None
    assert any(e.field == "income" for e in errs)


def test_validate_empty_name():
    pr, errs = validate_row_dict(
        5,
        {"id": "1", "name": "  ", "age": "25", "city": "SP", "income": "0"},
    )
    assert pr is None
    assert any(e.field == "name" for e in errs)


def test_parse_valid_file():
    csv_text = "id,name,age,city,income\n1,A,20,X,1000\n"
    rows, total, errors = parse_csv_content(csv_text.encode("utf-8"))
    assert total == 1
    assert len(rows) == 1
    assert errors == []


def test_parse_skips_invalid_rows():
    csv_text = (
        "id,name,age,city,income\n"
        "1,OK,25,X,1000\n"
        "2,,25,X,1000\n"
    )
    rows, total, errors = parse_csv_content(csv_text.encode("utf-8"))
    assert total == 2
    assert len(rows) == 1
    assert len(errors) >= 1


def test_parse_wrong_headers():
    csv_text = "id,name,age,city,bad\n1,A,20,X,1\n"
    with pytest.raises(ValueError, match="headers"):
        parse_csv_content(csv_text.encode("utf-8"))


def test_parse_empty_body():
    csv_text = "id,name,age,city,income\n"
    rows, total, errors = parse_csv_content(csv_text.encode("utf-8"))
    assert total == 0
    assert rows == []


def test_parse_utf8_bom():
    csv_text = "\ufeffid,name,age,city,income\n1,A,20,X,0\n"
    rows, total, _ = parse_csv_content(csv_text.encode("utf-8-sig"))
    assert total == 1
    assert len(rows) == 1
