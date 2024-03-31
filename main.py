import redis.asyncio as redis
import uvicorn
from dotenv import load_dotenv
from fastapi import Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, MissingTokenError
from fastapi_limiter import FastAPILimiter
from starlette.responses import JSONResponse

from custom_fast_api import CustomFastAPI
from src.cache.async_redis import get_redis
from src.conf.config import settings
from src.routes import users, auth, photos, transform_photos, rates, comments

app = CustomFastAPI()


@app.on_event("startup")
async def startup():
    r = await get_redis()
    await FastAPILimiter.init(r)


app.include_router(users.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(transform_photos.router, prefix="/api")
app.include_router(rates.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=401,
        content={
            "message": f"Invalid user authorization credentials or token is expired"
        },
    )


@app.exception_handler(MissingTokenError)
async def missing_token_exception_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=401,
        content={"message": "Authorization token wasn't sent"},
    )


if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(app, host="127.0.0.1", port=8000)
