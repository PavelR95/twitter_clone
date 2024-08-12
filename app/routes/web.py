from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from ..application import DIRECTORY_MEDIA, DIRECTORY_TEMPLATES

web_router = APIRouter()
templates = Jinja2Templates(directory=DIRECTORY_TEMPLATES)


@web_router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Возвращает иконку сайта

    Returns:
        FileResponse: фал картинки
    """
    return FileResponse("{dir_media}/favicon.ico".format(dir_media=DIRECTORY_MEDIA))


@web_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def hello(request: Request):
    """Возвращает страницу сайта 

    Args:
        request (Request): Объект запроса

    Returns:
        TemplateResponse: рендерит шаблон и возвращает html код
    """
    return templates.TemplateResponse(request=request, name="index.html")


@web_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def hello(request: Request):
    """Возвращает страницу сайта 

    Args:
        request (Request): Объект запроса

    Returns:
        TemplateResponse: рендерит шаблон и возвращает html код
    """
    return templates.TemplateResponse(request=request, name="index.html")


@web_router.get(
    "/profile/{path:path}", response_class=HTMLResponse, include_in_schema=False
)
async def hello(request: Request):
    """Возвращает страницу сайта 

    Args:
        request (Request): Объект запроса

    Returns:
        TemplateResponse: рендерит шаблон и возвращает html код
    """
    return templates.TemplateResponse(
        request=request, name="index.html", context={"id": id}
    )
