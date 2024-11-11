from typing import Protocol


class RawMessage(Protocol):
    seq: int
    msg_chain: list
