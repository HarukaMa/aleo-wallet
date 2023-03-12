from ..chain_db import ChainDB
from ..events.events import EventDispatcher, EventType, Event
from ..utils.types import InitPhase


class WalletCore:

    def __init__(self):
        self.event_dispatcher = EventDispatcher()

    async def start(self):
        self.chain_db = await ChainDB.open(self.event_dispatcher)
        await self.event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.Finish))

    async def stop(self):
        await self.chain_db.close()
