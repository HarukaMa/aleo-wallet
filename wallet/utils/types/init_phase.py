import enum


class InitPhase(enum.IntEnum):
    OpenChainDB = 0
    CreateChainDB = 5
    CheckChainDB = 10
    OpenWalletDB = 20
    Finish = 100
