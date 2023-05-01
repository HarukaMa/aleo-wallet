from wallet.events import EventDispatcher


# lame name
class Syncer:

    def __init__(self, event_dispatcher: EventDispatcher):
        self.event_dispatcher = EventDispatcher()
