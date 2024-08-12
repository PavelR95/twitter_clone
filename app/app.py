from . import application
from .routes import api, web

app = application.get_app(debug_mod=application.settings.DEBUG_MOD)

# Register routers
app.include_router(web.web_router)
app.include_router(api.api_routes)
