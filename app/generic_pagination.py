from fastapi import Request
from sqlalchemy.orm import Query


def paginate_query(request: Request, query: Query, page: int = 1, page_size: int = 10):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    base_url = str(request.url).split("?")[0]

    def build_url(page_num: int):
        return f"{base_url}?page={page_num}&page_size={page_size}"

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
