from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int]
    role: Optional[str]


class UserCreate(BaseModel):
    mobile: str
    password: str
    role: str  # "manager" or "worker"


class UserOut(BaseModel):
    id: int
    mobile: str
    role: str

    class Config:
        orm_mode = True


# --- Tasks ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int  # worker id


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    assigned_to: int
    assigned_by: int

    class Config:
        orm_mode = True


class TaskStatusUpdate(BaseModel):
    status: str  # pending | in_progress | completed


# --- Pagination response ---
T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    count: int
    page: int
    page_size: int
    next: Optional[str]
    previous: Optional[str]
    results: List[T]
