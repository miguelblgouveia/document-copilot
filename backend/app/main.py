import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        # Interactive environments (Jupyter/VS Code Interactive) already own the loop.
        loop.create_task(uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000)).serve())

