from fastapi import FastAPI

from app.database import Base, engine
from app.routers.project_member_router import router as project_member_router
from app.routers.project_router import router as project_router
from app.routers.tasks_router import router as tasks_router
from app.routers.user_router import router as user_router

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Database tables created"}


# Projects
app.include_router(project_router)

# Users
app.include_router(user_router)

# Tasks
app.include_router(tasks_router)

# Project Members
app.include_router(project_member_router)
