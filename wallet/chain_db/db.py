import os

import aiosqlite
import appdirs

from ..events import EventDispatcher, Event, EventType
from ..utils.types import InitPhase


class ChainDB:

    def __init__(self):
        self.db_path = None
        self.conn = None
        self.closed = False

    @classmethod
    async def open(cls, event_dispatcher: EventDispatcher, data_path=None):
        await event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.OpenChainDB))
        if data_path is None:
            # noinspection PyTypeChecker
            data_path = appdirs.user_data_dir("WalletDev", False)
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self = cls()
        self.db_path = data_path + "/chain.db"
        if not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
            await event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.CreateChainDB))
            await self.create_db()
        self.conn = await aiosqlite.connect(self.db_path, isolation_level=None)
        self.conn.row_factory = aiosqlite.Row
        await event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.CheckChainDB))
        errors = await self.check_database()
        if errors:
            raise RuntimeError("chain database integrity check failed: " + str(errors))
        return self

    async def close(self):
        if self.closed:
            return
        self.closed = True
        await self.conn.close()

    async def check_database(self) -> None | list:
        async with self.conn.execute("pragma integrity_check;") as cursor:
            result = await cursor.fetchall()
            if result[0]["integrity_check"] != "ok":
                return result

    async def create_db(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.executescript(open("init.sql").read())
