from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine as Engine
from app.database.connection import Base
from app.database import models
from core.config import settings

from app.routers.config_api import config_router
from app.routers.user_api import user_router


app = FastAPI()

app = FastAPI(title=settings.title, description=settings.description, version=settings.version,swagger_ui_parameters={"docExpansion": "none"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    from core.logs import logger
    logger.info("Starting up the application...")
    Base.metadata.create_all(bind=Engine)



app.include_router(config_router,tags=["config"],prefix="/config")
app.include_router(user_router,tags=["user"],prefix="")
app.include_router(admin_router,tags=["Admin"],prefix="")