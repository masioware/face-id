from fastapi import FastAPI

from app.controllers import enroll, identify

def create_app() -> FastAPI:
    app = FastAPI()

    # routes
    app.include_router(identify.router)
    app.include_router(enroll.router)

    return app
