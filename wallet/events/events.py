import asyncio
from collections import defaultdict
from enum import IntEnum

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QApplication
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property


class EventType(IntEnum):
    InitStep = QEvent.register_event_type()
    WalletLock = QEvent.register_event_type()


class Event:
    def __init__(self, type_: EventType, content: any):
        self.type = type_
        self.content = content


class QtEvent(QEvent):
    def __init__(self, event: Event):
        super().__init__(QEvent.Type(event.type.value))
        self.event = event


class EventDispatcher:
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.event_handlers = defaultdict(lambda: [])
        self.event_receivers = []
        asyncio.create_task(self.dispatch_events())

    def register_event_handler(self, event_type: EventType, handler):
        self.event_handlers[event_type].append(handler)

    def unregister_event_handler(self, event_type: EventType, handler):
        self.event_handlers[event_type].remove(handler)

    def register_qt_event_receiver(self, receiver: QObject):
        self.event_receivers.append(receiver)

    async def post_event(self, event: Event):
        await self.event_queue.put(event)

    async def dispatch_events(self):
        while True:
            event = await self.event_queue.get()
            for handler in self.event_handlers[event.type]:
                await handler(event)
            qt_event = QtEvent(event)
            for receiver in self.event_receivers:
                QApplication.post_event(receiver, qt_event)


# noinspection PyMissingConstructor
class DummyEventDispatcher(EventDispatcher):
    def __init__(self):
        pass

    async def post_event(self, event: Event):
        pass
