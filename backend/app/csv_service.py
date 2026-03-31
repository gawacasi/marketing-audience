from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass

from app.schemas import RowError

logger = logging.getLogger(__name__)

EXPECTED_HEADERS = ("id", "name", "age", "city", "income")


@dataclass
class ParsedRow:
    customer_id: int
    name: str
    age: int
    city: str
    income: float


def validate_row_dict(row_num: int, row: dict[str, str]) -> tuple[ParsedRow | None, list[RowError]]:
    errors: list[RowError] = []

    def add(field: str, message: str) -> None:
        errors.append(RowError(row=row_num, field=field, message=message))

    raw_id = (row.get("id") or "").strip()
    if not raw_id:
        add("id", "id is required")
    else:
        try:
            cid = int(raw_id)
            if cid <= 0:
                add("id", "id must be a positive integer")
        except ValueError:
            add("id", "id must be a positive integer")
            cid = 0

    name = (row.get("name") or "").strip()
    if not name:
        add("name", "name cannot be empty")

    raw_age = (row.get("age") or "").strip()
    if not raw_age:
        add("age", "age is required")
    else:
        try:
            age = int(raw_age)
            if age <= 0:
                add("age", "age must be a positive integer")
        except ValueError:
            add("age", "age must be a positive integer")
            age = 0

    city = (row.get("city") or "").strip()
    if not city:
        add("city", "city cannot be empty")

    raw_income = (row.get("income") or "").strip()
    if not raw_income:
        add("income", "income is required")
    else:
        try:
            income = float(raw_income)
            if income < 0:
                add("income", "income must be a non-negative number")
        except ValueError:
            add("income", "income must be a non-negative number")
            income = 0.0

    if errors:
        return None, errors

    return (
        ParsedRow(
            customer_id=int(raw_id),
            name=name,
            age=int(raw_age),
            city=city,
            income=float(raw_income),
        ),
        [],
    )


def parse_csv_content(
    content: bytes, upload_id: str | None = None
) -> tuple[list[ParsedRow], int, list[RowError]]:
    """
    Returns (valid_rows, total_data_rows, errors). Header row not counted in total_data_rows.
    Raises ValueError for malformed file / wrong headers (caller maps to 422).
    """
    log_prefix = f"upload_id={upload_id}" if upload_id else "csv"
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        logger.warning("%s CSV decode failed: %s", log_prefix, e)
        raise ValueError("unparseable file encoding") from e

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("empty or missing CSV headers")

    normalized = [h.strip().lower() if h else "" for h in reader.fieldnames]
    if tuple(normalized) != EXPECTED_HEADERS:
        logger.warning(
            "%s wrong headers: got %s expected %s",
            log_prefix,
            normalized,
            EXPECTED_HEADERS,
        )
        raise ValueError(
            f"CSV must have headers exactly: {', '.join(EXPECTED_HEADERS)}"
        )

    valid: list[ParsedRow] = []
    errors: list[RowError] = []
    total = 0
    for i, row in enumerate(reader, start=2):
        total += 1
        norm_row = {k.strip().lower(): (v or "") for k, v in row.items() if k}
        parsed, row_errs = validate_row_dict(i, norm_row)
        if parsed:
            valid.append(parsed)
        errors.extend(row_errs)

    logger.info(
        "%s CSV parsed: total_rows=%s valid=%s invalid=%s",
        log_prefix,
        total,
        len(valid),
        total - len(valid),
    )
    return valid, total, errors
