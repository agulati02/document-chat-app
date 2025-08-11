import logging
from fastapi import FastAPI
from routers import user_router
from utils.bootstrap import lifespan

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(lifespan=lifespan)
app.include_router(user_router.router, prefix="/v1/users")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
