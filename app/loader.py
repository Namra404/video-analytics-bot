import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime  # <-- добавляем

from sqlalchemy import text

from app.core.db import async_session_maker

logger = logging.getLogger(__name__)


def parse_dt(value: str) -> datetime:
    """
    функция для приведения к datetime
    """
    return datetime.fromisoformat(value)


async def load_json(path: str = "/app/data/videos.json") -> None:
    logger.info("Loading JSON from %s", path)
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)

    videos_rows = []
    snapshots_rows = []

    items = data.get("videos", data)

    for video in items:
        videos_rows.append(
            {
                "id": video["id"],
                "creator_id": video["creator_id"],
                "video_created_at": parse_dt(video["video_created_at"]),
                "views_count": video["views_count"],
                "likes_count": video["likes_count"],
                "comments_count": video["comments_count"],
                "reports_count": video["reports_count"],
                "created_at": parse_dt(video["created_at"]),
                "updated_at": parse_dt(video["updated_at"]),
            }
        )

        for snap in video["snapshots"]:
            snapshots_rows.append(
                {
                    "id": snap["id"],
                    "video_id": video["id"],
                    "views_count": snap["views_count"],
                    "likes_count": snap["likes_count"],
                    "comments_count": snap["comments_count"],
                    "reports_count": snap["reports_count"],
                    "delta_views_count": snap["delta_views_count"],
                    "delta_likes_count": snap["delta_likes_count"],
                    "delta_comments_count": snap["delta_comments_count"],
                    "delta_reports_count": snap["delta_reports_count"],
                    "created_at": parse_dt(snap["created_at"]),
                    "updated_at": parse_dt(snap["updated_at"]),
                }
            )

    insert_videos_sql = text("""
        INSERT INTO videos (
            id, creator_id, video_created_at,
            views_count, likes_count, comments_count, reports_count,
            created_at, updated_at
        )
        VALUES (
            :id, :creator_id, :video_created_at,
            :views_count, :likes_count, :comments_count, :reports_count,
            :created_at, :updated_at
        )
        ON CONFLICT (id) DO NOTHING
    """)

    insert_snapshots_sql = text("""
        INSERT INTO video_snapshots (
            id, video_id,
            views_count, likes_count, comments_count, reports_count,
            delta_views_count, delta_likes_count,
            delta_comments_count, delta_reports_count,
            created_at, updated_at
        )
        VALUES (
            :id, :video_id,
            :views_count, :likes_count, :comments_count, :reports_count,
            :delta_views_count, :delta_likes_count,
            :delta_comments_count, :delta_reports_count,
            :created_at, :updated_at
        )
        ON CONFLICT (id) DO NOTHING
    """)

    async with async_session_maker() as session:
        async with session.begin():
            logger.info("Inserting %d videos", len(videos_rows))
            if videos_rows:
                await session.execute(insert_videos_sql, videos_rows)

            logger.info("Inserting %d snapshots", len(snapshots_rows))
            if snapshots_rows:
                await session.execute(insert_snapshots_sql, snapshots_rows)

    logger.info("JSON data loaded successfully")


if __name__ == "__main__":
    from app.core.logging_conf import setup_logging
    setup_logging()
    asyncio.run(load_json())
