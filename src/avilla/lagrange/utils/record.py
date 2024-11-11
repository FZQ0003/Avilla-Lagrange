import time
from dataclasses import dataclass, field

from lagrange.client.message.types import Element


@dataclass
class MessageRecord:
    friend_uin: int
    seq: int
    msg_chain: list[Element]
    group_uin: int = 0
    target_uin: int = 0  # to record sent message
    msg_id: int = 0
    time: int = field(default_factory=lambda: int(time.time()))

    def __post_init__(self):
        # Only generate for messages with no msg_id / rand
        if not self.msg_id:
            if self.group_uin:
                self.msg_id = hash((self.group_uin, self.seq))
            else:
                # Seq here may vary for different accounts and may not be unique
                self.msg_id = hash((self.friend_uin, self.seq))

    @property
    def msg(self) -> str:
        return ''.join(getattr(_, 'text', '') or _.display for _ in self.msg_chain)

    # TODO: FriendInfo GroupMemberInfo MessageHash

    @property
    def msg_hash(self) -> int:
        return hash(self)

    def __hash__(self) -> int:  # same as core
        part_1 = (self.msg_id & 65535).to_bytes(2, byteorder='little')
        part_2 = (self.seq & 65535).to_bytes(2, byteorder='little')
        return int.from_bytes(part_1 + part_2, byteorder='little', signed=True)
