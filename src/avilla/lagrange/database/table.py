from dataclasses import field
from datetime import datetime

from sqlalchemy import BIGINT, CHAR, ForeignKey
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from .types import Base, BigTimestamp, JsonText


class UserInfo(MappedAsDataclass, Base):
    __tablename__ = 'user_info'

    uin: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    uid: Mapped[str] = mapped_column(CHAR(24))

    # groups: list['GroupMemberInfo'] = field(init=False)
    received_records: list['MessageRecord'] = field(init=False)
    sent_records: list['MessageRecord'] = field(init=False)


class GroupInfo(MappedAsDataclass, Base):
    __tablename__ = 'group_info'

    uin: Mapped[int] = mapped_column(BIGINT, primary_key=True)

    # members: list['GroupMemberInfo'] = field(init=False)
    records: list['MessageRecord'] = field(init=False)


# class GroupMemberInfo(MappedAsDataclass, Base):
#     __tablename__ = 'group_member_info'
# 
#     group_uin: Mapped[int] = mapped_column(ForeignKey(GroupInfo.uin), primary_key=True)
#     member_uin: Mapped[int] = mapped_column(ForeignKey(UserInfo.uin), primary_key=True)
#     role: Mapped[int] = mapped_column(BIGINT, default=0)
# 
#     group: Mapped[GroupInfo] = relationship(
#         GroupInfo, backref='members', foreign_keys=[group_uin], init=False
#     )
#     member: Mapped[UserInfo] = relationship(
#         UserInfo, backref='groups', foreign_keys=[member_uin], init=False
#     )


class MessageRecord(MappedAsDataclass, Base):
    __tablename__ = 'message_record'

    friend_uin: Mapped[int] = mapped_column(ForeignKey(UserInfo.uin))
    seq: Mapped[int] = mapped_column(BIGINT)
    msg_chain: Mapped[list] = mapped_column(JsonText)  # list[Element]
    group_uin: Mapped[int] = mapped_column(ForeignKey(GroupInfo.uin), default=0)
    target_uin: Mapped[int] = mapped_column(ForeignKey(UserInfo.uin), default=0)  # to record sent message
    msg_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, default=0)  # rand in group, msg_id in friend
    time: Mapped[datetime] = mapped_column(BigTimestamp, default_factory=datetime.now)

    friend: Mapped[UserInfo] = relationship(
        UserInfo, backref='received_records', foreign_keys=[friend_uin], init=False
    )
    group: Mapped[GroupInfo | None] = relationship(
        GroupInfo, backref='records', foreign_keys=[group_uin], init=False
    )
    target: Mapped[UserInfo | None] = relationship(
        UserInfo, backref='sent_records', foreign_keys=[target_uin], init=False
    )

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
        return ''.join(_.display for _ in self.msg_chain)

    # TODO: FriendInfo GroupMemberInfo MessageHash

    @property
    def msg_hash(self) -> int:
        return hash(self)

    def __hash__(self) -> int:  # same as core
        part_1 = (self.msg_id & 65535).to_bytes(2, byteorder='little')
        part_2 = (self.seq & 65535).to_bytes(2, byteorder='little')
        return int.from_bytes(part_1 + part_2, byteorder='little', signed=True)
