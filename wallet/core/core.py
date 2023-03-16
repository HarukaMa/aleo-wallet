from ..chain_db import ChainDB
from ..core import HDWallet
from ..events.events import EventDispatcher, EventType, Event
from ..utils.types import InitPhase


class WalletCore:

    def __init__(self):
        self.event_dispatcher = EventDispatcher()

    async def start(self):
        self.chain_db = await ChainDB.open(self.event_dispatcher)
        self.wallet = await HDWallet.open(self.event_dispatcher)
        if self.wallet is None:
            await self.event_dispatcher.post_event(Event(EventType.NoWallet, None))
        await self.event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.Finish))

    async def stop(self):
        await self.chain_db.close()

    async def reload_wallet(self) -> bool:
        self.wallet = await HDWallet.open(self.event_dispatcher)
        return self.wallet is not None
