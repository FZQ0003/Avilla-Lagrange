from avilla.core.elements import (
    Audio,
    Face,
    Notice,
    NoticeAll,
    Picture,
    Reference,
    Text,
    Video,
)
# from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.standard.qq.elements import (
    App,
    # Dice,
    FlashImage,
    # Gift,
    Json,
    # MusicShare,
    Poke,
    # Share,
    Xml,
    MarketFace,
)
# from lagrange.client.client import Client
from lagrange.client.message.elems import (
    Text as LgrText,
    Quote as LgrQuote,
    Json as LgrJson,
    # Service as LgrService,
    AtAll as LgrAtAll,
    At as LgrAt,
    Image as LgrImage,
    Video as LgrVideo,
    Audio as LgrAudio,
    Raw as LgrRaw,
    Emoji as LgrEmoji,
    # Reaction as LgrReaction,
    Poke as LgrPoke,
    MarketFace as LgrMarketFace,
    # File as LgrFile,
)

from ..base import LagrangePerform
from ...capability import LagrangeCapability
from ...const import TEXT_AT_ALL
from ...resource import LagrangeResource


class LagrangeMessageSerializePerform(LagrangePerform):

    @LagrangeCapability.serialize_element.collect(element=Text)
    async def text(self, element: Text) -> LgrText:
        return LgrText(text=element.text)

    @LagrangeCapability.serialize_element.collect(element=Face)
    async def face(self, element: Face) -> LgrEmoji:
        return LgrEmoji(id=int(element.id))

    # TODO: resource and more...

    @LagrangeCapability.serialize_element.collect(element=Picture)
    async def picture(self, element: Picture) -> LgrImage | None:
        # client: Client = self.connection.client
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res
        # if self.context:
        #     ...

    @LagrangeCapability.serialize_element.collect(element=Audio)
    async def audio(self, element: Audio) -> LgrAudio | None:
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res

    @LagrangeCapability.serialize_element.collect(element=Video)
    async def video(self, element: Video) -> LgrVideo | None:
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res

    @LagrangeCapability.serialize_element.collect(element=FlashImage)
    async def flash_image(self, element: FlashImage) -> LgrImage | None:
        return await self.picture(element)  # type: ignore

    @LagrangeCapability.serialize_element.collect(element=Notice)
    async def notice(self, element: Notice) -> LgrAt:
        uin = int(element.target['member'])
        uid = (await self.database.get_user(uin)).uid
        return LgrAt(uin=uin, uid=uid, text=f"{element.display or ''}")

    @LagrangeCapability.serialize_element.collect(element=NoticeAll)
    async def notice_all(self, element: NoticeAll) -> LgrAtAll:
        return LgrAtAll(text=TEXT_AT_ALL)

    @LagrangeCapability.serialize_element.collect(element=Reference)
    async def reply(self, element: Reference) -> LgrQuote | None:
        # TODO: reply
        if group_uin := int(element.message.pattern.get('group', 0)):
            friend_uin = int(element.message.pattern.get('member', 0))
        else:
            friend_uin = int(element.message.pattern.get('friend', 0))
        record = await self.database.get_msg_record(
            msg_id=int(element.message['message']),
            seq=int(element.message['message']),
            friend_uin=friend_uin,
            group_uin=group_uin
        )
        return LgrQuote(
            seq=record.seq,
            uin=record.friend_uin,
            timestamp=int(record.time.timestamp()),
            uid=record.friend.uid,
            msg=record.msg
        )

    # @LagrangeCapability.serialize_element.collect(element=Dice)
    # async def dice(self, element: Dice) -> ...:
    #     return ...

    # TODO: dice, music_share, gift

    @LagrangeCapability.serialize_element.collect(element=Poke)
    async def poke(self, element: Poke) -> LgrPoke:
        return LgrPoke(id=1)  # shake

    @LagrangeCapability.serialize_element.collect(element=Json)
    async def json(self, element: Json) -> LgrJson:
        code = element.content.encode()
        return LgrJson(raw=code)

    @LagrangeCapability.serialize_element.collect(element=Xml)
    async def xml(self, element: Xml) -> LgrRaw:  # TODO: sure (xml)?
        code = element.content.encode()
        return LgrRaw(data=code)

    @LagrangeCapability.serialize_element.collect(element=App)
    async def app(self, element: App | Json) -> LgrJson:
        return await self.json(element)  # type: ignore

    # TODO: share

    @LagrangeCapability.serialize_element.collect(element=MarketFace)
    async def market_face(self, element: MarketFace) -> LgrMarketFace:
        return LgrMarketFace(
            name=element.summary or '[]',
            face_id=bytes.fromhex(element.id),
            tab_id=int(element.tab_id or 0),
            width=200,
            height=200
        )
