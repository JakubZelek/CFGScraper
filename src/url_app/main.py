from contextlib import asynccontextmanager
from fastapi import FastAPI
from url_app.api.routers.process_url import router as events_router
from url_app.api.dependencies import elastic_manager, url_app_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await elastic_manager.index_exists(url_app_settings.elastic_index):
        await elastic_manager.create_index(url_app_settings.elastic_index)
    yield

app = FastAPI(title=url_app_settings.app_name, debug=url_app_settings.debug, lifespan=lifespan)
app.include_router(events_router)
