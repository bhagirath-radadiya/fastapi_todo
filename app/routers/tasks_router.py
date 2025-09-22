from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app import models, schemas
from app.constant import MAX_PAGE_SIZE
from app.deps import get_current_user, get_db, require_manager
from app.generic_pagination import paginate_query
from app.helpers import safe_commit

router = APIRouter(prefix="", tags=["tasks"])


# ----------------- Endpoints -----------------
@router.get("/workers/", response_model=schemas.PaginatedResponse[schemas.UserOut])
def list_workers(
    request: Request,
    page: int = 1,
    page_size: int = Query(10, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    manager=Depends(require_manager),
):
    q = (
        db.query(models.User)
        .filter(models.User.role == "worker")
        .order_by(models.User.id)
    )
    return paginate_query(request, q, page, page_size)


@router.post("/tasks/", response_model=schemas.TaskOut)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    manager=Depends(require_manager),
):
    worker = (
        db.query(models.User)
        .filter(models.User.id == task_in.assigned_to, models.User.role == "worker")
        .first()
    )
    if not worker:
        raise HTTPException(status_code=400, detail="Worker not found")
    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        status="pending",
        assigned_to=task_in.assigned_to,
        assigned_by=manager.id,
    )
    db.add(task)
    safe_commit(db)
    db.refresh(task)
    return task


@router.get("/tasks/my", response_model=schemas.PaginatedResponse[schemas.TaskOut])
def my_tasks(
    request: Request,
    page: int = 1,
    page_size: int = Query(10, le=MAX_PAGE_SIZE),
    status: Union[str, None] = Query(None, description="pending/in_progress/completed"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "worker":
        q = (
            db.query(models.Task)
            .filter(models.Task.assigned_to == current_user.id)
            .order_by(models.Task.id)
        )
    else:
        q = (
            db.query(models.Task)
            .filter(models.Task.assigned_by == current_user.id)
            .order_by(models.Task.id)
        )
    if status and status in (
        models.TaskStatus.pending.value,
        models.TaskStatus.in_progress.value,
        models.TaskStatus.completed.value,
    ):
        q = q.filter(models.Task.status == status)
    return paginate_query(request, q, page, page_size)


@router.patch("/tasks/{task_id}/status", response_model=schemas.TaskOut)
def update_status(
    task_id: int,
    status_in: schemas.TaskStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if user.role == "worker" and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if status_in.status not in ("pending", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")
    task.status = status_in.status
    db.add(task)
    safe_commit(db)
    db.refresh(task)
    return task
