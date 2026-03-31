from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.errors import not_found
from app.database import get_db
from app.deps import Page, PageSize, pagination_offset
from app.models import Campaign, CampaignUser, User
from app.schemas import (
    CampaignDetail,
    CampaignSummary,
    CampaignUsersResponse,
    Paginated,
    UserOut,
)

router = APIRouter()


@router.get("/campaigns", response_model=Paginated[CampaignSummary])
def list_campaigns(
    db: Session = Depends(get_db),
    page: Page = 1,
    page_size: PageSize = 20,
    upload_id: str | None = Query(None, description="Scope stats to users from this upload"),
):
    offset, limit = pagination_offset(page, page_size)

    total = db.execute(select(func.count()).select_from(Campaign)).scalar() or 0

    rows = db.execute(
        select(Campaign).order_by(Campaign.id).offset(offset).limit(limit)
    ).scalars().all()

    data: list[CampaignSummary] = []
    for c in rows:
        q = (
            select(func.count(User.id), func.coalesce(func.avg(User.income), 0.0))
            .select_from(CampaignUser)
            .join(User, User.id == CampaignUser.user_id)
            .where(CampaignUser.campaign_id == c.id)
        )
        if upload_id:
            q = q.where(User.upload_id == upload_id)
        cnt, avg_inc = db.execute(q).one()
        data.append(
            CampaignSummary(
                id=c.id,
                name=c.name,
                users_count=int(cnt or 0),
                average_income=float(avg_inc or 0),
            )
        )

    return Paginated[CampaignSummary](data=data, page=page, page_size=page_size, total=total)


@router.get("/campaigns/{campaign_id}", response_model=CampaignUsersResponse)
def get_campaign_users(
    campaign_id: int,
    db: Session = Depends(get_db),
    page: Page = 1,
    page_size: PageSize = 20,
):
    c = db.get(Campaign, campaign_id)
    if c is None:
        not_found(f"Campaign with id {campaign_id} was not found")

    cnt, avg_inc = db.execute(
        select(func.count(User.id), func.coalesce(func.avg(User.income), 0.0))
        .select_from(CampaignUser)
        .join(User, User.id == CampaignUser.user_id)
        .where(CampaignUser.campaign_id == campaign_id)
    ).one()

    offset, limit = pagination_offset(page, page_size)

    count_q = (
        select(func.count())
        .select_from(CampaignUser)
        .where(CampaignUser.campaign_id == campaign_id)
    )
    total_users = db.execute(count_q).scalar() or 0

    user_ids = (
        db.execute(
            select(User.id)
            .join(CampaignUser, CampaignUser.user_id == User.id)
            .where(CampaignUser.campaign_id == campaign_id)
            .order_by(User.id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    users = db.execute(select(User).where(User.id.in_(user_ids))).scalars().all()
    by_id = {u.id: u for u in users}
    ordered = [by_id[i] for i in user_ids if i in by_id]

    return CampaignUsersResponse(
        campaign=CampaignDetail(
            id=c.id,
            name=c.name,
            users_count=int(cnt or 0),
            average_income=float(avg_inc or 0),
        ),
        users=Paginated[UserOut](
            data=[UserOut.model_validate(u) for u in ordered],
            page=page,
            page_size=page_size,
            total=total_users,
        ),
    )
