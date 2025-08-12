import logging
from fastapi import FastAPI
from routers import user_router

from utils.bootstrap import lifespan
from exceptions.user_exceptions import UserNotFoundException
from exceptions.handlers import UserExceptionHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router, prefix="/v1/users")

app.add_exception_handler(UserNotFoundException, UserExceptionHandler.handle_user_not_found_exception)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
