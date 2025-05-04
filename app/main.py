from fastapi import FastAPI

from app.settings import settings
from app.routes import router

app = FastAPI()

app.include_router(router)


# TODO
# 1. For each request, validate the users in middleware. If the user is valid, store the user ID and the organisation ID
#    in the request state. The user ID and organisation ID are stored in the database.


@app.get("/")
async def get_settings():
    return settings.project_root
