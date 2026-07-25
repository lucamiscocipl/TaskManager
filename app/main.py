import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.realtime.redis_notifications import (
    listen_for_notifications,
    redis_publisher,
    redis_subscriber,
)
from app.routers.notifications_router import router as notifications_router
from app.routers.project_member_router import router as project_member_router
from app.routers.project_router import router as project_router
from app.routers.task_comments_router import router as task_comments_router
from app.routers.task_image_router import router as task_image_router
from app.routers.tasks_router import router as tasks_router
from app.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    subscriber_task = asyncio.create_task(listen_for_notifications())

    yield

    subscriber_task.cancel()
    with suppress(asyncio.CancelledError):
        await subscriber_task

    await redis_subscriber.aclose()
    redis_publisher.close()


app = FastAPI(lifespan=lifespan)

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

# Notifications
app.include_router(notifications_router)
