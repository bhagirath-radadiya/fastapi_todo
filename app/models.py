import enum

from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ---------------- Enums ----------------
class UserRole(enum.Enum):
    manager = "manager"
    worker = "worker"


class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# ---------------- User Model ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="userrole", native_enum=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # relationships
    tasks_assigned_to = relationship(
        "Task",
        foreign_keys="Task.assigned_to",
        back_populates="assignee",
        cascade="all, delete-orphan",
    )
    tasks_assigned_by = relationship(
        "Task",
        foreign_keys="Task.assigned_by",
        back_populates="assigner",
        cascade="all, delete-orphan",
    )


# ---------------- Task Model ----------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(TaskStatus, name="taskstatus", native_enum=True),
        default=TaskStatus.pending,
        nullable=False,
    )

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # relationships
    assignee = relationship(
        "User", foreign_keys=[assigned_to], back_populates="tasks_assigned_to"
    )
    assigner = relationship(
        "User", foreign_keys=[assigned_by], back_populates="tasks_assigned_by"
    )
