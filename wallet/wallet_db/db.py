import hashlib
import os

import aiosqlite
import appdirs
from Crypto.Cipher import AES

from ..events import EventDispatcher, Event, EventType
from ..utils.types import InitPhase


class WalletDB:

    def __init__(self):
        self.db_path = None
        self.conn = None
        self.closed = False
        self.unlocked = False
        self.master_key = None

    @classmethod
    async def open(cls, event_dispatcher: EventDispatcher, data_path=None):
        await event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.OpenWalletDB))
        if data_path is None:
            # noinspection PyTypeChecker
            data_path = appdirs.user_data_dir("WalletDev", False)
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self = cls()
        self.db_path = data_path + "/wallet.db"
        if not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
            # trigger onboarding on None
            return None
        self.conn = await aiosqlite.connect(self.db_path, isolation_level=None)
        self.conn.row_factory = aiosqlite.Row
        await event_dispatcher.post_event(Event(EventType.InitStep, InitPhase.CheckWalletDB))
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

    async def unlock(self, password: str):
        if self.closed:
            raise RuntimeError("wallet is closed")
        if self.unlocked:
            return True
        async with self.conn.execute("SELECT salt FROM salt") as cursor:
            salt = (await cursor.fetchone())[0]
        wallet_key = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=16, p=1, maxmem=2 ** 28, dklen=32)
        async with self.conn.execute("SELECT key FROM master_wallet_key") as cursor:
            master_key = (await cursor.fetchone())[0]
        try:
            self.master_key = self.decrypt(master_key, wallet_key)
        except (ValueError, KeyError):
            return False
        self.unlocked = True
        return True

    async def lock(self):
        if self.closed:
            raise RuntimeError("wallet is closed")
        if not self.unlocked:
            return
        self.master_key = None
        self.unlocked = False

    async def get_master_seed(self) -> bytes:
        if not self.unlocked:
            raise RuntimeError("wallet is locked")
        async with self.conn.execute("SELECT seed FROM master_seed") as cursor:
            return self.decrypt((await cursor.fetchone())[0])

    async def get_max_used_index(self) -> int:
        if not self.unlocked:
            raise RuntimeError("wallet is locked")
        async with self.conn.execute("SELECT `index` FROM max_used_index") as cursor:
            return (await cursor.fetchone())[0] or 0

    async def set_max_used_index(self, index: int):
        if not self.unlocked:
            raise RuntimeError("wallet is locked")
        await self.conn.execute("UPDATE max_used_index SET index = ?", (index,))

    def decrypt(self, ciphertext, key=None) -> bytes:
        if len(ciphertext) < 48:
            raise ValueError("ciphertext is too short")
        if key is None:
            key = self.master_key
        iv = ciphertext[:16]
        tag = ciphertext[-16:]
        ciphertext = ciphertext[16:-16]
        aes = AES.new(key, AES.MODE_GCM, iv)
        return aes.decrypt_and_verify(ciphertext, tag)

    def encrypt(self, plaintext, key=None) -> bytes:
        if key is None:
            key = self.master_key
        iv = os.urandom(16)
        aes = AES.new(key, AES.MODE_GCM, iv)
        ciphertext, tag = aes.encrypt_and_digest(plaintext)
        return aes.nonce + ciphertext + tag

    async def destroy(self):
        """WARNING: This should only be used during wallet creation!"""
        if self.closed:
            raise RuntimeError("wallet is closed")
        await self.conn.close()
        os.remove(self.db_path)

    @classmethod
    async def create_db(cls, password: str, master_seed: bytes, data_path=None):
        if data_path is None:
            # noinspection PyTypeChecker
            data_path = appdirs.user_data_dir("WalletDev", False)
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self = cls()
        self.db_path = data_path + "/wallet.db"
        if os.path.exists(self.db_path):
            raise FileExistsError("wallet database already exists")
        self.master_key = os.urandom(32)
        salt = os.urandom(32)
        wallet_key = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=16, p=1, maxmem=2 ** 28, dklen=32)
        enc_master_key = self.encrypt(self.master_key, wallet_key)
        self.conn = await aiosqlite.connect(self.db_path, isolation_level=None)
        await self.conn.executescript(open("init.sql").read())
        await self.conn.execute("INSERT INTO salt (salt) VALUES (?)", (salt,))
        await self.conn.execute("INSERT INTO master_wallet_key (key) VALUES (?)", (enc_master_key,))
        await self.conn.execute("INSERT INTO master_seed (seed) VALUES (?)", (self.encrypt(master_seed),))
        return self
