import base64
import os
import secrets

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from api.routes.admin import router as admin_router
from api.routes.apoios import router as apoios_router
from api.routes.relatos import router as relatos_router
from database.connection import init_database


app = FastAPI(
    title="Moove API",
    version="0.1.0",
    description="API backend for the Cadê Meu Ônibus campaign.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8002",
        "http://127.0.0.1:8002",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def is_admin_authenticated(authorization: str | None) -> bool:
    if not authorization or not authorization.startswith("Basic "):
        return False

    try:
        encoded_credentials = authorization.removeprefix("Basic ").strip()
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
    except (ValueError, UnicodeDecodeError):
        return False

    expected_username = os.getenv("ADMIN_USERNAME", "admin")
    expected_password = os.getenv("ADMIN_PASSWORD", "99440882")

    return secrets.compare_digest(username, expected_username) and secrets.compare_digest(
        password, expected_password
    )


@app.middleware("http")
async def protect_admin_routes(request, call_next):
    is_admin_route = request.url.path.startswith("/admin") or request.url.path.startswith(
        "/api/admin"
    )

    if is_admin_route and not is_admin_authenticated(request.headers.get("Authorization")):
        return Response(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Moove Admin"'},
        )

    return await call_next(request)


app.include_router(apoios_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(relatos_router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    init_database()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")
app.mount("/", StaticFiles(directory="public", html=True), name="public")
