import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.database import Base, engine
from app.routers import auth_router, tasks_router

# ---------------- Logging Setup ----------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------- Environment Variables ----------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")  # change in production
JWT_LOGIN_URL = os.getenv("JWT_LOGIN_URL", "login")  # login endpoint

# ---------------- FastAPI Instance ----------------
app = FastAPI(
    title="Todo App (Manager/Worker)",
    description="API for managing tasks with JWT authentication",
    version="1.0.0",
)

# ---------------- CORS Middleware ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routers ----------------
app.include_router(auth_router.router)
app.include_router(tasks_router.router)

# ---------------- OAuth2 JWT Scheme ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=JWT_LOGIN_URL)


# ---------------- Startup / Shutdown Events ----------------
@app.on_event("startup")
def startup_event():
    # Only for development, production should use Alembic migrations
    logger.info("Application startup: checking DB tables...")
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutdown")


# ---------------- Global Exception Handler ----------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error"})


# ---------------- Root Endpoint ----------------
@app.get("/", tags=["Root"])
def root():
    return {"message": "Todo App API is running"}


# ---------------- Custom OpenAPI for JWT ----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add JWT auth globally
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
