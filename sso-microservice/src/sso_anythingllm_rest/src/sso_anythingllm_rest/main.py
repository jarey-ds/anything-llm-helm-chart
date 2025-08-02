"""Main entry point for the API."""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kink import di
from loguru import logger
from pyctuator.endpoints import Endpoints
from pyctuator.health.db_health_provider import DbHealthProvider
from pyctuator.pyctuator import Pyctuator

from sso_anythingllm_facade.setup_di import setup_di as setup_facade_di
from sso_anythingllm_repository.setup_di import setup_di as setup_repository_di
from sso_anythingllm_rest import __version__ as app_version

# Import routers
from sso_anythingllm_rest.endpoints import sso
from sso_anythingllm_rest.setup_di import setup_di as setup_rest_di
from sso_anythingllm_service.setup_di import setup_di as setup_service_di


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting AnythingLLM SSO Integration API...")
    yield
    logger.info("Shutting down AnythingLLM SSO Integration API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Initial version, something we can really improve.
    logger.info("Setting up dependency injection...")
    setup_repository_di()
    setup_service_di()
    setup_facade_di()
    setup_rest_di()
    logger.info("Dependency injection finished....")
    app_name: str = "AnythingLLM SSO Integration API"

    app = FastAPI(
        title=app_name,
        description="API for managing AI model configurations and providers",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize routers
    # Register more specific routes first to avoid route conflicts
    sso.init_app(app, prefix="/api")

    pyctuator = Pyctuator(
        app,
        app_name=app_name,
        app_url="/api",
        registration_url=None,
        pyctuator_endpoint_url="/monitoring",
        disabled_endpoints={
            Endpoints.ENV,
            Endpoints.LOGFILE,
            Endpoints.HTTP_TRACE,
            Endpoints.LOGGERS,
            Endpoints.THREAD_DUMP,
            Endpoints.METRICS,
        },
    )

    # We rely on dependency injection to inject the existing repository from context
    # (second argument that is not passed to the HealthMonitor instance)
    pyctuator.register_health_provider(
        provider=DbHealthProvider(name="SSO AnythingLLM Database", engine=di["sync_engine"])
    )
    pyctuator.set_build_info(name=app_name, version=app_version)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    # Use import string to avoid double instantiation with reload
    uvicorn.run(
        app=app,
        host=host,
        port=port,
        reload=False,
        log_level="info",
        factory=False,  # factory=True is only needed if you use a function, not an app instance
    )
