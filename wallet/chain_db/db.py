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
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.CheckChainDB))
        await self.check_database()
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
            await conn.executescript("""
            
create table record_index
(
    id           integer           not null
        constraint record_index_pk
            primary key autoincrement,
    block_height integer           not null,
    is_private   integer default 0 not null,
    owner        blob              not null,
    nonce        blob              not null
);

create table full_record
(
    id       integer not null
        constraint full_record_pk
            primary key autoincrement,
    index_id integer not null
        constraint full_record_record_index_id_fk
            references record_index,
    record   blob    not null
);

create index record_index_is_private_index
    on record_index (is_private);

create index record_index_owner_index
    on record_index (owner);

create table version
(
    version integer not null
);

insert into version (version) values (1);

""")
