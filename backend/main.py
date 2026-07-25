import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_application() -> FastAPI:
    app = FastAPI(
        title="AI Atlas API",
        description="Backend API for AI Atlas application",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    import os
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = get_application()

from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Database operation failed."},
    )


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AI Atlas API")
    try:
        import os
        from core.database import Base, engine
        import models
        # Ensure database directory exists if using relative SQLite path
        db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
        if db_dir and not os.path.isabs(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified and created successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    # from scheduler import start_scheduler
    # start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    pass
    # from scheduler import stop_scheduler
    # stop_scheduler()

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint.
    """
    # Check DB connection
    db_status = "disconnected"
    try:
        from core.database import engine
        with engine.connect() as connection:
            db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "version": "1.0.0",
        "environment": "development"
    }

from routes.v1 import api_router

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
