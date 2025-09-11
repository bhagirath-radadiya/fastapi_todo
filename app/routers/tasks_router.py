from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..deps import get_db, require_manager, require_worker, get_current_user

router = APIRouter(prefix="", tags=["tasks"])

def paginate_query(query, page: int = 1, page_size: int = 10):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}

# Manager: list workers
@router.get("/workers/", response_model=schemas.PaginatedResponse)
def list_workers(page: int = 1, page_size: int = 10, db: Session = Depends(get_db), manager = Depends(require_manager)):
    q = db.query(models.User).filter(models.User.role == "worker").order_by(models.User.id)
    res = paginate_query(q, page, page_size)
    res["items"] = [{"id": u.id, "mobile": u.mobile, "role": u.role} for u in res["items"]]
    return res

# Manager: assign task
@router.post("/tasks/", response_model=schemas.TaskOut)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db), manager = Depends(require_manager)):
    worker = db.query(models.User).filter(models.User.id == task_in.assigned_to, models.User.role=="worker").first()
    if not worker:
        raise HTTPException(status_code=400, detail="Worker not found")
    task = models.Task(title=task_in.title, description=task_in.description, status="pending", assigned_to=task_in.assigned_to, assigned_by=manager.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# Worker or Manager: list their tasks
@router.get("/tasks/my", response_model=schemas.PaginatedResponse)
def my_tasks(page: int = 1, page_size: int = 10, 
             status: str | None = Query(None, description="Filter tasks by status: pending/in_progress/completed"),
             db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role == 'worker':
        q = db.query(models.Task).filter(models.Task.assigned_to == current_user.id).order_by(models.Task.id)
    else:
        q = db.query(models.Task).filter(models.Task.assigned_by == current_user.id).order_by(models.Task.id)
    if status and status in ("pending", "in_progress", "completed"):
        q = q.filter(models.Task.status == status)
    res = paginate_query(q, page, page_size)
    res["items"] = [{"id": t.id, "title": t.title, "description": t.description, "status": t.status, "assigned_to": t.assigned_to} for t in res["items"]]
    return res

# Worker: update status
@router.patch("/tasks/{task_id}/status", response_model=schemas.TaskOut)
def update_status(task_id: int, status_in: schemas.TaskStatusUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id==task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if user.role=="worker" and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if status_in.status not in ("pending", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")
    task.status = status_in.status
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
