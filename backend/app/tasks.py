from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Campaign, CampaignUser, Upload, User
from app.segmentation import ALL_CAMPAIGNS, UserSegmentInput, campaigns_for_user

logger = logging.getLogger(__name__)


def ensure_campaigns(db: Session) -> dict[str, int]:
    name_to_id: dict[str, int] = {}
    for name in ALL_CAMPAIGNS:
        row = db.execute(select(Campaign).where(Campaign.name == name)).scalar_one_or_none()
        if row is None:
            row = Campaign(name=name)
            db.add(row)
            db.flush()
        name_to_id[name] = row.id
    return name_to_id


def run_campaign_generation(upload_id: str) -> dict[str, int]:
    db = SessionLocal()
    try:
        up = db.get(Upload, upload_id)
        if user_ids:
            db.execute(delete(CampaignUser).where(CampaignUser.user_id.in_(user_ids)))
        counts: dict[str, int] = {n: 0 for n in ALL_CAMPAIGNS}
        for u in users:
            for cname in campaigns_for_user(UserSegmentInput(age=u.age, income=u.income)):
                db.add(CampaignUser(user_id=u.id, campaign_id=name_to_id[cname]))
                counts[cname] += 1
        up.status = "completed"
        up.processed_at = datetime.utcnow()
        db.commit()
        logger.info("upload_id=%s inline campaign generation counts=%s", upload_id, counts)
        return counts
    except Exception:
        logger.exception("upload_id=%s campaign generation failed", upload_id)
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.generate_campaigns_for_upload")
def generate_campaigns_for_upload(self, upload_id: str) -> dict[str, int]:
    logger.info(
        "upload_id=%s background job started task_id=%s",
        upload_id,
        getattr(self.request, "id", None),
    )
    db = SessionLocal()
    try:
        up = db.get(Upload, upload_id)
        if up is None:
            logger.error("upload_id=%s not found in worker", upload_id)
            return {}

        name_to_id = ensure_campaigns(db)
        users = list(db.execute(select(User).where(User.upload_id == upload_id)).scalars().all())
        user_ids = [u.id for u in users]
        if user_ids:
            db.execute(delete(CampaignUser).where(CampaignUser.user_id.in_(user_ids)))

        counts: dict[str, int] = {n: 0 for n in ALL_CAMPAIGNS}
        for u in users:
            for cname in campaigns_for_user(UserSegmentInput(age=u.age, income=u.income)):
                db.add(CampaignUser(user_id=u.id, campaign_id=name_to_id[cname]))
                counts[cname] += 1

        up.status = "completed"
        up.processed_at = datetime.utcnow()
        db.commit()

        logger.info(
            "upload_id=%s background job completed campaign generation results=%s",
            upload_id,
            counts,
        )
        return counts
    except Exception:
        logger.exception("upload_id=%s background job failed", upload_id)
        db.rollback()
        _mark_upload_failed(upload_id)
        raise
    finally:
        db.close()


def _mark_upload_failed(upload_id: str) -> None:
    db = SessionLocal()
    try:
        up = db.get(Upload, upload_id)
        if up:
            up.status = "failed"
            up.processed_at = datetime.utcnow()
            db.commit()
    except Exception:
        logger.exception("upload_id=%s could not mark upload failed", upload_id)
        db.rollback()
    finally:
        db.close()
