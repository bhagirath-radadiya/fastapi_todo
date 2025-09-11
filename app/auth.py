from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from .schemas import TokenData

SECRET_KEY = "CHANGE_THIS_SECRET_TO_SOMETHING_SAFE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30   # Access token 30 min valid
REFRESH_TOKEN_EXPIRE_DAYS = 7      # Refresh token 7 din valid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Password ----------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ---------------- Token Create ----------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- Token Decode ----------------
def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return TokenData(user_id=None, role=None)

def decode_refresh_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return TokenData(user_id=None, role=None)
