import hmac
import os
from hashlib import sha512

from mnemonic import Mnemonic

from ..events import EventDispatcher
from ..wallet_db import WalletDB

MASTER_SEED = b"bls12_377 seed"


def parse_path(path: str) -> [int]:
    path = path.strip()
    if path == "m":
        return []
    if path.startswith("m/"):
        path = path[2:]
    path = path.split("/")
    if any("'" not in x for x in path):
        raise ValueError("only hardened paths are supported")
    return [int(x[:-1]) + 0x80000000 for x in path]


def get_path_string(path: [int]) -> str:
    if not path:
        return "m"
    return "m/" + "/".join([str(x - 0x80000000) + "'" for x in path])

def get_path_string_assume_hardened(path: [int]) -> str:
    if not path:
        return "m"
    return "m/" + "/".join([str(x) + "'" for x in path])

def _generate_master_node(seed) -> [bytes, bytes]:
    h = hmac.new(MASTER_SEED, digestmod=sha512)
    h.update(seed)
    digest = h.digest()
    return digest[:32], digest[32:]


def _generate_key(seed: [bytes, bytes], index: int) -> [bytes, bytes]:
    h = hmac.new(seed[1], digestmod=sha512)
    h.update(b"\x00" + seed[0] + index.to_bytes(4, "big"))
    digest = h.digest()
    return digest[:32], digest[32:]


class HDWallet:
    def __init__(self, db: WalletDB):
        self.seed = None
        self._seed_cache: dict[str, [bytes, bytes]] = {}
        self.wallet_db = db
        self.closed = False

    @classmethod
    async def create_wallet(cls, password: str, strength: int = 128):
        seed = os.urandom(strength // 8)
        if _generate_master_node(seed)[0] == b"\x00" * 32:
            seed = os.urandom(strength // 8)
            # you can't be this unlucky
        return cls(await WalletDB.create_db(password, seed))

    @classmethod
    async def create_wallet_from_mnemonic(cls, password: str, mnemonic: str):
        seed = Mnemonic("english").to_entropy(mnemonic)
        return cls(await WalletDB.create_db(password, seed))

    @classmethod
    async def open(cls, event_dispatcher: EventDispatcher):
        db = await WalletDB.open(event_dispatcher)
        if db is None:
            return None
        return cls(db)

    async def unlock(self, password: str):
        if await self.wallet_db.unlock(password):
            self.seed = await self.wallet_db.get_master_seed()
            return True
        return False

    async def close(self):
        await self.wallet_db.close()
        self.closed = True

    async def destroy(self):
        """WARNING: This should only be used during wallet creation!"""
        await self.wallet_db.destroy()
        self.closed = True

    def to_mnemonic(self) -> str:
        return Mnemonic("english").to_mnemonic(self.seed)

    def get_seed_for_path(self, path: str) -> [bytes, bytes]:
        if path in self._seed_cache:
            return self._seed_cache[path]
        path = parse_path(path)
        if not path:
            return self._seed_cache["m"]
        if get_path_string(path[:-1]) not in self._seed_cache:
            self._seed_cache[get_path_string(path[:-1])] = self.get_seed_for_path(get_path_string(path[:-1]))
        seed = _generate_key(self._seed_cache[get_path_string(path[:-1])], path[-1])
        self._seed_cache[get_path_string(path)] = seed
        return seed
