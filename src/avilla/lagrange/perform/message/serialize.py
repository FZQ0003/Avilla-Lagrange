from typing import TYPE_CHECKING

from avilla.core import Context
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
from avilla.core.ryanvk.collector.account import AccountCollector
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
from graia.ryanvk import OptionalAccess
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

from .elements import MarketFaceEx
from ...capability import LagrangeCapability
from ...const import TEXT_AT_ALL
from ...resource import LagrangeResource
from ...service import LagrangeDatabase

if TYPE_CHECKING:
    from ...account import LagrangeAccount  # noqa: F401
    from ...protocol import LagrangeProtocol  # noqa: F401


class LagrangeMessageSerializePerform((m := AccountCollector['LagrangeProtocol', 'LagrangeAccount']())._):
    m.namespace = 'avilla.protocol/lagrange::message'
    m.identify = 'serialize'

    context: OptionalAccess[Context] = OptionalAccess()

    @m.entity(LagrangeCapability.serialize_element, element=Text)  # type: ignore
    async def text(self, element: Text) -> LgrText:
        return LgrText(text=element.text)

    @m.entity(LagrangeCapability.serialize_element, element=Face)  # type: ignore
    async def face(self, element: Face) -> LgrEmoji:
        return LgrEmoji(id=int(element.id))

    # TODO: resource and more...

    @m.entity(LagrangeCapability.serialize_element, element=Picture)  # type: ignore
    async def picture(self, element: Picture) -> LgrImage | None:
        # client: Client = self.connection.client
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res
        # if self.context:
        #     ...

    @m.entity(LagrangeCapability.serialize_element, element=Audio)  # type: ignore
    async def audio(self, element: Audio) -> LgrAudio | None:
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res

    @m.entity(LagrangeCapability.serialize_element, element=Video)  # type: ignore
    async def video(self, element: Video) -> LgrVideo | None:
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res

    @m.entity(LagrangeCapability.serialize_element, element=FlashImage)  # type: ignore
    async def flash_image(self, element: FlashImage) -> LgrImage | None:
        return await self.picture(element)  # type: ignore

    @m.entity(LagrangeCapability.serialize_element, element=Notice)  # type: ignore
    async def notice(self, element: Notice) -> LgrAt:
        uin = int(element.target['member'])
        db: LagrangeDatabase = self.protocol.service.database
        return LgrAt(uin=uin, uid=db.get_user(uin)[1], text=f"{element.display or ''}")

    @m.entity(LagrangeCapability.serialize_element, element=NoticeAll)  # type: ignore
    async def notice_all(self, element: NoticeAll) -> LgrAtAll:
        return LgrAtAll(text=TEXT_AT_ALL)

    @m.entity(LagrangeCapability.serialize_element, element=Reference)  # type: ignore
    async def reply(self, element: Reference) -> LgrQuote | None:
        # TODO: reply
        if group_uin := int(element.message.pattern.get('group', 0)):
            friend_uin = int(element.message.pattern.get('member', 0))
        else:
            friend_uin = int(element.message.pattern.get('friend', 0))
        db: LagrangeDatabase = self.protocol.service.database
        record = db.get_msg_record(
            msg_id=int(element.message['message']),
            seq=int(element.message['message']),
            friend_uin=friend_uin,
            group_uin=group_uin
        )
        return LgrQuote(
            seq=record.seq,
            uin=record.friend_uin,
            timestamp=record.time,
            uid=db.get_user(record.friend_uin)[1],
            msg=record.msg
        )

    # @m.entity(LagrangeCapability.serialize_element, element=Dice)
    # async def dice(self, element: Dice) -> ...:
    #     return ...

    # TODO: dice, music_share, gift

    @m.entity(LagrangeCapability.serialize_element, element=Poke)  # type: ignore
    async def poke(self, element: Poke) -> LgrPoke:
        return LgrPoke(id=1)  # shake

    @m.entity(LagrangeCapability.serialize_element, element=Json)  # type: ignore
    async def json(self, element: Json) -> LgrJson:
        code = element.content.encode()
        return LgrJson(raw=code)

    @m.entity(LagrangeCapability.serialize_element, element=Xml)  # type: ignore
    async def xml(self, element: Xml) -> LgrRaw:  # TODO: sure (xml)?
        code = element.content.encode()
        return LgrRaw(data=code)

    @m.entity(LagrangeCapability.serialize_element, element=App)  # type: ignore
    async def app(self, element: App | Json) -> LgrJson:
        return await self.json(element)  # type: ignore

    # TODO: share

    @m.entity(LagrangeCapability.serialize_element, element=MarketFace)  # type: ignore
    async def market_face(self, element: MarketFace) -> LgrMarketFace:
        tab_id = getattr(element, 'tab_id', MarketFaceEx.tab_id)
        width = getattr(element, 'width', MarketFaceEx.width)
        height = getattr(element, 'height', MarketFaceEx.height)
        return LgrMarketFace(
            name=element.name or '[]',
            face_id=bytes.fromhex(element.id),
            tab_id=tab_id,
            width=width,
            height=height
        )
