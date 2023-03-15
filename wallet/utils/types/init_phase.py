import enum


class InitPhase(enum.IntEnum):
    OpenChainDB = 0
    CreateChainDB = 5
    CheckChainDB = 10
    OpenWalletDB = 20
    CreateWalletDB = 25
    CheckWalletDB = 30
    Finish = 100
