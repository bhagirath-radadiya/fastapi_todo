from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from fastapi import Request
from sqlalchemy.orm import Query

from app.constant import DEFAULT_PAGE_SIZE


def paginate_query(
    request: Request, query: Query, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE
):
    page = max(page, 1)
    page_size = max(page_size, 1)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    # Preserve base URL and existing query params
    url_parts = urlparse(str(request.url))
    query_params = parse_qs(url_parts.query)

    def build_url(page_num: int):
        query_params_updated = {
            **query_params,
            "page": [str(page_num)],
            "page_size": [str(page_size)],
        }
        return urlunparse(
            url_parts._replace(query=urlencode(query_params_updated, doseq=True))
        )

    next_url = build_url(page + 1) if (page * page_size) < total else None
    prev_url = build_url(page - 1) if page > 1 else None

    return {
        "count": total,
        "page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": items,
    }
