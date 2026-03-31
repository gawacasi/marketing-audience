import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    filename: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="upload")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("uploads.id", ondelete="CASCADE"), index=True
    )
    customer_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(512))
    age: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(256))
    income: Mapped[float] = mapped_column(Float)

    upload: Mapped["Upload"] = relationship("Upload", back_populates="users")
    campaign_links: Mapped[list["CampaignUser"]] = relationship(
        "CampaignUser", back_populates="user"
    )

    __table_args__ = (UniqueConstraint("upload_id", "customer_id", name="uq_user_upload_customer"),)


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)

    users: Mapped[list["CampaignUser"]] = relationship(
        "CampaignUser", back_populates="campaign"
    )


class CampaignUser(Base):
    __tablename__ = "campaign_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    campaign_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="campaign_links")
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="users")

    __table_args__ = (
        UniqueConstraint("user_id", "campaign_id", name="uq_campaign_user_pair"),
    )
