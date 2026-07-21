from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.project_member_router import router as project_member_router
from app.routers.project_router import router as project_router
from app.routers.task_comments_router import router as task_comments_router
from app.routers.task_image_router import router as task_image_router
from app.routers.tasks_router import router as tasks_router
from app.routers.user_router import router as user_router

app = FastAPI()

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Database tables created"}


# Projects
app.include_router(project_router)

# Users
app.include_router(user_router)

# Tasks
app.include_router(tasks_router)

# Task Images
app.include_router(task_image_router)

# Project Members
app.include_router(project_member_router)

# Task Comments
app.include_router(task_comments_router)
