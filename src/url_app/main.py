from contextlib import asynccontextmanager
from fastapi import FastAPI
from url_app.api.routers.process_url import router as events_router
from url_app.api.dependencies import elastic_manager
from common.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await elastic_manager.index_exists(settings.elastic_index):
        await elastic_manager.create_index(settings.elastic_index)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(events_router)
