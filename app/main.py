from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import auth, users, financial, dashboard
from app.core.rate_limiter import limiter

# ─── Create all database tables on startup ───────────────────────────────────
Base.metadata.create_all(bind=engine)



# ─── Application ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Finance Dashboard API",
    description=(
        "## Role-aware Finance Backend\n\n"
        "A structured REST API for managing financial records with role-based access control.\n\n"
        "### Roles\n"
        "| Role | Capabilities |\n"
        "|---|---|\n"
        "| **viewer** | View records and recent activity |\n"
        "| **analyst** | viewer + create records + access dashboard analytics |\n"
        "| **admin** | Full access — manage users, update/delete records |\n\n"
        "### Authentication\n"
        "Use `POST /auth/login` to obtain a JWT token, then click **Authorize** "
        "and enter: `Bearer <your_token>`"
    ),
    version="1.0.0",
    contact={"name": "Finance Dashboard Team"},
    license_info={"name": "MIT"},
)

# ─── Rate Limiting & Middleware Setup ─────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(financial.router)
app.include_router(dashboard.router)


# ─── Global Exception Handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal error occurred."},
    )


# ─── Root / Health Endpoints ──────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="API root")
def root():
    return {
        "status": "ok",
        "message": "Finance Dashboard API is running.",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    return {"status": "healthy"}
