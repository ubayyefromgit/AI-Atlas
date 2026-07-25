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
        
        # Auto-seed initial dataset if company directory is empty
        def auto_seed_if_empty():
            from core.database import SessionLocal
            from models.company import Company
            db = SessionLocal()
            try:
                company_count = db.query(Company).count()
                if company_count == 0:
                    logger.info("No companies found in database. Starting initial dataset ingestion & index build...")
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    data_dir = os.path.join(root_dir, "data", "atlas_dataset")
                    
                    if os.path.exists(data_dir):
                        from services.ingestion.loader import CSVLoader
                        from services.ingestion.importer import DataImporter
                        from services.ingestion.report import ImportReport
                        
                        loader = CSVLoader(data_dir=data_dir)
                        df_sectors = loader.load_csv("sectors_reference.csv")
                        df_companies = loader.load_csv("companies_germany.csv")
                        df_problems = loader.load_csv("problems_germany.csv")
                        df_mappings = loader.load_csv("problem_company_mapping.csv")
                        
                        report = ImportReport()
                        importer = DataImporter(db=db, report=report, dry_run=False)
                        importer.import_sectors(df_sectors)
                        importer.import_companies(df_companies)
                        importer.import_problems(df_problems)
                        importer.import_mappings(df_mappings)
                        db.commit()
                        logger.info(f"Dataset ingested successfully: {db.query(Company).count()} companies imported.")
                        
                        # Build Knowledge Base Index
                        try:
                            from services.knowledge_base.indexer import KnowledgeBaseIndexer
                            indexer = KnowledgeBaseIndexer(db)
                            indexer.index_sectors()
                            indexer.index_companies()
                            indexer.index_problems()
                            logger.info("Knowledge base vector index built successfully.")
                        except Exception as idx_err:
                            logger.error(f"Failed to build vector index: {idx_err}")
                    else:
                        logger.warning(f"Data directory not found at: {data_dir}")
                else:
                    logger.info(f"Database already populated with {company_count} companies.")
            except Exception as seed_err:
                db.rollback()
                logger.error(f"Error during dataset auto-seeding: {seed_err}")
            finally:
                db.close()
                
        auto_seed_if_empty()
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    # from scheduler import start_scheduler
    # start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    pass
    # from scheduler import stop_scheduler
    # stop_scheduler()

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Atlas API is running",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR
    }

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
