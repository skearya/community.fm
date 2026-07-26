from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite
from loguru import logger

if TYPE_CHECKING:
    from state import State


@dataclass(frozen=True)
class User:
    id: int
    lastfm_username: str
    lastfm_session: str


class Db:
    def __init__(self, state: State):
        self.db = aiosqlite.connect(state.config.DATABASE_FILEPATH)

    async def connect(self):
        await self.db

        async with self.db.execute("PRAGMA user_version") as cursor:
            (version,) = await cursor.fetchone() or (0,)

        migrations = sorted(
            (Path(__file__).parent / "migrations").resolve().glob("*.sql")
        )

        for migration in migrations[version:]:
            content = migration.read_text()

            logger.info(f"Applying migration {migration.name}")
            await self.db.executescript(content)

    async def close(self):
        await self.db.close()

    async def create_user(self, id: int, lastfm_username: str, lastfm_session: str):
        await self.db.execute(
            "INSERT INTO users (id, lastfm_username, lastfm_session) VALUES (?, ?, ?)",
            (id, lastfm_username, lastfm_session),
        )
        await self.db.commit()

    async def get_user(self, id: int) -> User | None:
        async with self.db.execute("SELECT * FROM users WHERE id = ?", (id,)) as cursor:
            row = await cursor.fetchone()
            return User(*row) if row else None

    async def get_users(self) -> list[User]:
        async with self.db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [User(*row) for row in rows]

    async def update_user(self, id: int, lastfm_username: str, lastfm_session: str):
        await self.db.execute(
            "UPDATE users SET lastfm_username = ?, lastfm_session = ? WHERE id = ?",
            (lastfm_username, lastfm_session, id),
        )
        await self.db.commit()

    async def delete_user(self, id: int):
        await self.db.execute("DELETE FROM users WHERE id = ?", (id,))
        await self.db.commit()
