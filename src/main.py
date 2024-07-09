import os
import sys

import dotenv
from fastapi import FastAPI

import src.app.models
from src.app.router import router
from src.database import engine

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="TraceIt")


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(src.app.models.Base.metadata.drop_all)
        await conn.run_sync(src.app.models.Base.metadata.create_all)


app.include_router(router, prefix="/api/v1", tags=["app"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", reload=True, port=8080)
