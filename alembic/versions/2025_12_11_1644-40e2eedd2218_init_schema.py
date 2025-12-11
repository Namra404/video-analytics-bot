"""init schema

Revision ID: 40e2eedd2218
Revises: 
Create Date: 2025-12-11 16:44:47.516083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40e2eedd2218'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id               TEXT PRIMARY KEY,
            creator_id       TEXT NOT NULL,
            video_created_at TIMESTAMPTZ NOT NULL,

            views_count      BIGINT NOT NULL,
            likes_count      BIGINT NOT NULL,
            comments_count   BIGINT NOT NULL,
            reports_count    BIGINT NOT NULL,

            created_at       TIMESTAMPTZ NOT NULL,
            updated_at       TIMESTAMPTZ NOT NULL
        );
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS video_snapshots (
            id                   TEXT PRIMARY KEY,
            video_id             TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

            views_count          BIGINT NOT NULL,
            likes_count          BIGINT NOT NULL,
            comments_count       BIGINT NOT NULL,
            reports_count        BIGINT NOT NULL,

            delta_views_count    BIGINT NOT NULL,
            delta_likes_count    BIGINT NOT NULL,
            delta_comments_count BIGINT NOT NULL,
            delta_reports_count  BIGINT NOT NULL,

            created_at           TIMESTAMPTZ NOT NULL,
            updated_at           TIMESTAMPTZ NOT NULL
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_videos_creator_created_at
            ON videos (creator_id, video_created_at);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_videos_views_count
            ON videos (views_count);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_created_at
            ON video_snapshots (created_at);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_video_id
            ON video_snapshots (video_id);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS video_snapshots;")
    op.execute("DROP TABLE IF EXISTS videos;")