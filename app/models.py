from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "manager" or "worker"

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


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending / in_progress / completed
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # relationships
    assignee = relationship(
        "User", foreign_keys=[assigned_to], back_populates="tasks_assigned_to"
    )
    assigner = relationship(
        "User", foreign_keys=[assigned_by], back_populates="tasks_assigned_by"
    )
