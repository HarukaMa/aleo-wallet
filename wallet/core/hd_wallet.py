import hmac
import secrets
from hashlib import sha512

from mnemonic import Mnemonic

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
    def __init__(self, seed: bytes):
        self.seed = seed
        self._seed_cache: dict[str, [bytes, bytes]] = {
            "m": _generate_master_node(seed)
        }

    @classmethod
    def generate(cls, strength: int = 256):
        seed = secrets.token_bytes(strength // 8)
        if _generate_master_node(seed)[0] == b"\x00" * 32:
            seed = secrets.token_bytes(strength // 8)
            # you can't be this unlucky
        return cls(seed)

    @classmethod
    def from_mnemonic(cls, mnemonic: str):
        return cls(Mnemonic("english").to_entropy(mnemonic))

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
