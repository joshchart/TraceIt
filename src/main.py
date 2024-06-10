import sys
import os
from fastapi import FastAPI
from src.devices.router import router as devices_router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

app.include_router(devices_router, prefix="/api/v1", tags=["devices"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
