from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from ai.api.routes.devsecops import router as devsecops_router
from ai.api.routes.analysis import router as analysis_router
from ai.api.routes.health import router as health_router
from ai.api.routes.ui import router as ui_router
from ai.database.postgres.repositories.analysis_repository import initialize_analysis_table
from ai.infrastructure.logging.logger import get_logger
from ai.infrastructure.logging.request_logger import log_request, log_response

logger = get_logger("sentinelai.api")
app = FastAPI(title="SentinelAI AI Service", version="1.1.0")

# Restrict this list to the actual local/deployed frontend origins.
origins = [x.strip() for x in __import__("os").getenv("SENTINELAI_FRONTEND_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])

app.include_router(analysis_router)
app.include_router(health_router)
app.include_router(devsecops_router)
app.include_router(ui_router)

@app.on_event("startup")
def startup():
    try:
        initialize_analysis_table()
        logger.info("SentinelAI PostgreSQL analysis table initialized.")
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    log_request(request.method, request.url.path)
    response = await call_next(request)
    log_response(request.method, request.url.path, response.status_code)
    return response

@app.get("/")
def root():
    return {"service": "SentinelAI AI Service", "status": "running", "message": "AI service is running successfully"}
