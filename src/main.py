import os
import sys

import dotenv
from fastapi import FastAPI

from src.app.router import router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="TraceIt")

app.include_router(router, prefix="/api/v1", tags=["app"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", reload=True, port=8080)
