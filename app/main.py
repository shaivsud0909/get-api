from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import Base, engine as Engine
from app.database import models
from core.config import settings

from app.routers.authentication_api import authentication_router
from app.authentication.role import admin_required, user_required
from app.routers.admin_api import admin_router
from app.routers.config_api import config_router
from app.routers.user_api import user_router

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    swagger_ui_parameters={"docExpansion": "none"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    from core.logs import logger

    logger.info("Starting up the application...")
    async with Engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(authentication_router, tags=["authentication"], prefix="")
app.include_router(user_router, tags=["user"], prefix="", dependencies=[Depends(user_required)])
app.include_router(admin_router, tags=["admin"], prefix="", dependencies=[Depends(admin_required)])
app.include_router(config_router, tags=["config"], prefix="/config")
