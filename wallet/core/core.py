import asyncio
import threading

from .hd_wallet import HDWallet
from ..chain_db import ChainDB
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

    # stop is called in aboutToQuit, but the main thread will be closed very shortly after that
    # so we need to run the stop task in a separate thread
    def stop(self):
        t = threading.Thread(target=self.stop_in_thread)
        t.start()

    async def stop_task(self):
        await self.chain_db.close()
        await self.wallet.close()

    def stop_in_thread(self):
        asyncio.run(self.stop_task())

    async def reload_wallet(self) -> bool:
        self.wallet = await HDWallet.open(self.event_dispatcher)
        return self.wallet is not None
