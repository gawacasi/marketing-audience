from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import Page, PageSize, pagination_offset
from app.models import User
from app.schemas import Paginated, UserOut

router = APIRouter()


@router.get("/users", response_model=Paginated[UserOut])
def list_users(
    db: Session = Depends(get_db),
    page: Page = 1,
    page_size: PageSize = 20,
    name: str | None = Query(None, description="Partial match (case-insensitive)"),
    min_age: int | None = Query(None, ge=0),
    max_age: int | None = Query(None, ge=0),
    min_income: float | None = Query(None, ge=0),
    max_income: float | None = Query(None, ge=0),
):
    offset, limit = pagination_offset(page, page_size)

    stmt = select(User)
    if name:
        stmt = stmt.where(User.name.ilike(f"%{name}%"))
    if min_age is not None:
        stmt = stmt.where(User.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(User.age <= max_age)
    if min_income is not None:
        stmt = stmt.where(User.income >= min_income)
    if max_income is not None:
        stmt = stmt.where(User.income <= max_income)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    rows = db.execute(
        stmt.order_by(User.id).offset(offset).limit(limit)
    ).scalars().all()

    return Paginated[UserOut](
        data=[UserOut.model_validate(u) for u in rows],
        page=page,
        page_size=page_size,
        total=total,
    )
