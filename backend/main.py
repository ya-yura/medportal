from contextlib import asynccontextmanager


from fastapi_users import FastAPIUsers
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api import router as api_router
from auth.manager import get_user_manager
from core.config import settings
from core.models.db_helper import db_helper
from core.connection import User
from core.logger import logger
from core.middleware import log_middleware
from auth.auth import auth_backend
from auth.schemas import UserCreate, UserRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


app = FastAPI(
    default_response_class=ORJSONResponse,
    title="MedPortal",
    lifespan=lifespan,
    )

app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
logger.info('Starting MedPortal API...')

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.run.host,
        port=settings.run.port,
    )
