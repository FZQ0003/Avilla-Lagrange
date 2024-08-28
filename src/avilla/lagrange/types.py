from typing import Union

from lagrange.client.events.service import (
    ClientOnline,
    ClientOffline,
    ServerKick,
)
from lagrange.client.events.group import (
    GroupMessage,
    GroupRecall,
    # GroupNudge,
    # GroupSign,
    # GroupMuteMember,
    # GroupMemberJoinRequest,
    # GroupMemberJoined,
    # GroupMemberQuit,
    # GroupMemberGotSpecialTitle,
    # GroupNameChanged,
    # GroupReaction,
    # GroupAlbumUpdate,
)
from lagrange.client.events.friend import (
    FriendMessage,
    # FriendNudge,
)
from lagrange.client.message.elems import (
    Text,
    Quote,
    Json,
    # Service,
    AtAll,
    At,
    Image,
    Video,
    Audio,
    Raw,
    Emoji,
    # Reaction,
    Poke,
    MarketFace,
)

AVAILABLE_EVENTS = (
    ClientOnline,
    ClientOffline,
    ServerKick,
    GroupMessage,
    GroupRecall,
    # GroupNudge,
    # GroupSign,
    # GroupMuteMember,
    # GroupMemberJoinRequest,
    # GroupMemberJoined,
    # GroupMemberQuit,
    # GroupMemberGotSpecialTitle,
    # GroupNameChanged,
    # GroupReaction,
    # GroupAlbumUpdate,
    FriendMessage,
    # FriendNudge,
)
Event = Union[AVAILABLE_EVENTS]

AVAILABLE_MSG_ELEMENTS = (
    Text,
    Quote,
    Json,
    # Service,
    AtAll,
    At,
    Image,
    Video,
    Audio,
    Raw,
    Emoji,
    # Reaction,
    Poke,
    MarketFace,
)
Element = Union[AVAILABLE_MSG_ELEMENTS]
