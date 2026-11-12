import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from zapcart_api.api.v1.router import api_router
from zapcart_api.core import settings
from zapcart_api.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s (env: %s)...", settings.app_name, settings.app_environment)
    yield
    logger.info("Shutting down %s...", settings.app_name)
    engine.dispose()
    logger.info("Database connection pool closed.")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.api_prefix)
