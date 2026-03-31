from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from enum import Enum

from pydantic import BaseModel, Field


class UploadStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

T = TypeVar("T")


class RowError(BaseModel):
    row: int
    field: str
    message: str


class UploadResponse(BaseModel):
    upload_id: str
    status: UploadStatus
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: list[RowError]


class UploadStatusResponse(BaseModel):
    id: str
    filename: str
    status: UploadStatus
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created_at: datetime
    processed_at: datetime | None


class Paginated(BaseModel, Generic[T]):
    data: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int


class CampaignSummary(BaseModel):
    id: int
    name: str
    users_count: int
    average_income: float


class UserOut(BaseModel):
    id: int
    upload_id: str
    customer_id: int
    name: str
    age: int
    city: str
    income: float

    model_config = {"from_attributes": True}


class CampaignDetail(BaseModel):
    id: int
    name: str
    users_count: int
    average_income: float


class CampaignUsersResponse(BaseModel):
    campaign: CampaignDetail
    users: Paginated[UserOut]


class ApiError(BaseModel):
    error: str
    message: str
    details: Any = None
