from typing import Any, Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    pages: int
    summary: dict[str, int] | None = None


def paginate(
    query: Any,
    *,
    page: int,
    page_size: int,
    summary: dict[str, int] | None = None,
) -> dict[str, Any]:
    total = query.order_by(None).count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size if total else 0,
        "summary": summary,
    }
