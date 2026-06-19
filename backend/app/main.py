import asyncio

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.auth.dependencies import AuthUser, get_current_user
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


@app.get("/auth/me")
async def me(user: AuthUser = Depends(get_current_user)):
    """Test authenticated endpoint — returns the caller's identity."""
    return {"id": user.id, "email": user.email}


@app.get("/teste")
async def teste():
    """Test."""
    return {"message": "This is a test endpoint."}


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        # Interactive environments (Jupyter/VS Code Interactive) already own the loop.
        loop.create_task(uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000)).serve())
