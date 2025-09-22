from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from app.routers import auth_router, tasks_router

# Create tables initially (optional if using alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo App (Manager/Worker)")

# Include routers
app.include_router(auth_router.router)
app.include_router(tasks_router.router)

# ---------------- Swagger UI JWT Token Integration ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # your login endpoint path


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Todo App (Manager/Worker)",
        version="1.0.0",
        description="API documentation with JWT authentication",
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
