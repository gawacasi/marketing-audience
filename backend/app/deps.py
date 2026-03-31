from typing import Annotated

from fastapi import Query

Page = Annotated[int, Query(ge=1, description="Page number (1-based)")]
PageSize = Annotated[int, Query(ge=1, le=100, description="Items per page")]


def pagination_offset(page: int, page_size: int) -> tuple[int, int]:
    return (page - 1) * page_size, page_size
