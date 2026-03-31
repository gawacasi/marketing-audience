from __future__ import annotations

import logging
from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors import bad_request, not_found, unprocessable
from app.csv_service import parse_csv_content
from app.database import get_db
from app.deps import Page, PageSize, pagination_offset
from app.models import Upload, User
from app.schemas import (
    Paginated,
    RowError,
    UploadResponse,
    UploadStatus,
    UploadStatusResponse,
)
from app.tasks import generate_campaigns_for_upload

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/uploads", response_model=Paginated[UploadStatusResponse])
def list_uploads(
    db: Session = Depends(get_db),
    page: Page = 1,
    page_size: PageSize = 100,
):
    total = db.execute(select(func.count()).select_from(Upload)).scalar() or 0
    offset, limit = pagination_offset(page, page_size)
    rows = (
        db.execute(
            select(Upload)
            .order_by(Upload.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    data = [
        UploadStatusResponse(
            id=u.id,
            filename=u.filename,
            status=UploadStatus(u.status),
            total_rows=u.total_rows,
            valid_rows=u.valid_rows,
            invalid_rows=u.invalid_rows,
            created_at=u.created_at,
            processed_at=u.processed_at,
        )
        for u in rows
    ]
    return Paginated[UploadStatusResponse](
        data=data, page=page, page_size=page_size, total=total
    )


@router.post("/upload", status_code=201, response_model=UploadResponse)
async def upload_csv(
    db: Session = Depends(get_db),
    file: Annotated[UploadFile | None, File()] = None,
):
    if file is None:
        bad_request("Missing file field", error="missing_file")
    if not file.filename or not file.filename.lower().endswith(".csv"):
        bad_request("Expected a .csv file", error="invalid_file_type")

    content = await file.read()
    if not content.strip():
        unprocessable("Empty file", error="empty_file")

    try:
        valid_rows, total, row_errors = parse_csv_content(content, upload_id=None)
    except ValueError as e:
        unprocessable(str(e), error="malformed_csv")

    seen: Counter[int] = Counter()
    for pr in valid_rows:
        seen[pr.customer_id] += 1
    dupes = [cid for cid, n in seen.items() if n > 1]
    if dupes:
        unprocessable(
            f"Duplicate customer id in file: {dupes[:10]}",
            error="duplicate_ids",
            details={"duplicate_ids": dupes[:50]},
        )

    upload_row = Upload(
        filename=file.filename,
        status="processing",
        total_rows=total,
        valid_rows=len(valid_rows),
        invalid_rows=total - len(valid_rows),
    )
    db.add(upload_row)
    db.flush()
    upload_id = upload_row.id

    logger.info(
        "upload_id=%s Upload received filename=%s row_count=%s",
        upload_id,
        file.filename,
        total,
    )

    for pr in valid_rows:
        db.add(
            User(
                upload_id=upload_id,
                customer_id=pr.customer_id,
                name=pr.name,
                age=pr.age,
                city=pr.city,
                income=pr.income,
            )
        )
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        unprocessable("Could not persist users (constraint violation)", details=str(e))

    generate_campaigns_for_upload.delay(upload_id)

    return UploadResponse(
        upload_id=upload_id,
        status=UploadStatus.processing,
        total_rows=total,
        valid_rows=len(valid_rows),
        invalid_rows=total - len(valid_rows),
        errors=[RowError.model_validate(e) for e in row_errors],
    )


@router.get("/upload/{upload_id}/status", response_model=UploadStatusResponse)
def get_upload_status(upload_id: str, db: Session = Depends(get_db)):
    up = db.get(Upload, upload_id)
    if up is None:
        not_found(f"Upload with id {upload_id} was not found")
    return UploadStatusResponse(
        id=up.id,
        filename=up.filename,
        status=UploadStatus(up.status),
        total_rows=up.total_rows,
        valid_rows=up.valid_rows,
        invalid_rows=up.invalid_rows,
        created_at=up.created_at,
        processed_at=up.processed_at,
    )
