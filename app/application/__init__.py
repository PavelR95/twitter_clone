from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..logger.logger import logger_app
from .custom_exp import CustomException
from .lifespan import lifespan, sql_manager
from .settings import settings

logger = logger_app

# Database Manager
SQL_MANAGER = sql_manager

# DIRECTORY WEB FILE SETTINGS
DIRECTORY_MEDIA = settings.DIRECTORY_MEDIA
DIRECTORY_TEMPLATES = settings.DIRECTORY_TEMPLATES
logger.info("DIRECTORY_MEDIA %s", DIRECTORY_MEDIA)
logger.info("DIRECTORY_TEMPLATES %s", DIRECTORY_TEMPLATES)


def get_app(debug_mod: bool = False):
    app = FastAPI(lifespan=lifespan, debug=debug_mod)
    # Statics Files
    app.mount("/css", StaticFiles(directory=f"{DIRECTORY_MEDIA}/css"), name="static")
    app.mount("/js", StaticFiles(directory=f"{DIRECTORY_MEDIA}/js"), name="static")
    app.mount(
        "/images", StaticFiles(directory=f"{DIRECTORY_MEDIA}/images"), name="static"
    )
    app

    # Custom exp
    @app.exception_handler(CustomException)
    async def custom_exp_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "result": False,
                "error_type": exc.error_type,
                "error_message": exc.error_message,
            },
        )

    return app
