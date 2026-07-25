import asyncio
import json
import logging
import os

import redis
import redis.asyncio as async_redis

from app.realtime.connection_manager import notification_connections

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
NOTIFICATION_CHANNEL = "task-manager:notifications"
logger = logging.getLogger(__name__)

redis_publisher = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

redis_subscriber = async_redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


def publish_notification(user_id: int, notification: dict) -> None:
    event = {
        "user_id": user_id,
        "payload": {
            "type": "notification.created",
            "data": notification,
        },
    }

    redis_publisher.publish(
        NOTIFICATION_CHANNEL,
        json.dumps(event),
    )


async def listen_for_notifications() -> None:
    while True:
        try:
            async with redis_subscriber.pubsub() as pubsub:
                await pubsub.subscribe(NOTIFICATION_CHANNEL)

                async for message in pubsub.listen():
                    if message["type"] != "message":
                        continue

                    event = json.loads(message["data"])

                    await notification_connections.send_to_user(
                        user_id=int(event["user_id"]),
                        payload=event["payload"],
                    )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception("Redis notification subscriber disconnected")
            await asyncio.sleep(2)
