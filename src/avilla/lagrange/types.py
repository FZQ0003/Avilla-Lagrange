from typing import Union, TypeAlias

from lagrange.client.events.friend import (
    FriendMessage,
    # FriendRecall,
    # FriendRequest,
    # FriendNudge,
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
    # GroupInvite,
    # GroupMemberJoinedByInvite,
)
from lagrange.client.events.service import (
    ClientOnline,
    ClientOffline,
    ServerKick,
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
    # File,
    # GreyTips,
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
    # GroupInvite,
    # GroupMemberJoinedByInvite,
    FriendMessage,
    # FriendRecall,
    # FriendRequest,
    # FriendNudge,
)
Event: TypeAlias = Union[
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
    # GroupInvite,
    # GroupMemberJoinedByInvite,
    FriendMessage,
    # FriendRecall,
    # FriendRequest,
    # FriendNudge,
]

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
    # File,
    # GreyTips,
)
Element: TypeAlias = Union[
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
    # File,
    # GreyTips,
]
