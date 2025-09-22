from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------- Register ----------------
@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if payload.role not in ("manager", "worker"):
        raise HTTPException(status_code=400, detail="role must be manager or worker")
    existing = (
        db.query(models.User).filter(models.User.mobile == payload.mobile).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Mobile already registered")
    user = models.User(
        mobile=payload.mobile,
        password_hash=auth.hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------- Login ----------------
@router.post("/login")
def login(
    mobile: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.mobile == mobile).first()
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = auth.create_access_token(
        data={"user_id": user.id, "role": user.role}
    )
    refresh_token = auth.create_refresh_token(
        data={"user_id": user.id, "role": user.role}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# ---------------- Refresh ----------------
@router.post("/refresh")
def refresh(refresh_token: str = Form(...)):
    token_data = auth.decode_refresh_token(refresh_token)
    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_access_token = auth.create_access_token(
        data={"user_id": token_data.user_id, "role": token_data.role}
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
