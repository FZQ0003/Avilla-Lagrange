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

    @m.entity(LagrangeCapability.serialize_element, element=Text)
    async def text(self, element: Text) -> LgrText:
        return LgrText(text=element.text)

    @m.entity(LagrangeCapability.serialize_element, element=Face)
    async def face(self, element: Face) -> LgrEmoji:
        return LgrEmoji(id=int(element.id))

    # TODO: resource and more...

    @m.entity(LagrangeCapability.serialize_element, element=Picture)
    async def picture(self, element: Picture) -> LgrImage | None:
        # client: Client = self.connection.client
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res
        # if self.context:
        #     ...

    @m.entity(LagrangeCapability.serialize_element, element=Audio)
    async def audio(self, element: Audio) -> LgrAudio | None:
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res

    @m.entity(LagrangeCapability.serialize_element, element=Video)
    async def video(self, element: Video) -> LgrVideo | None:
        if isinstance(element.resource, LagrangeResource):
            return element.resource.res

    @m.entity(LagrangeCapability.serialize_element, element=FlashImage)
    async def flash_image(self, element: FlashImage) -> LgrImage | None:
        return await self.picture(element)

    @m.entity(LagrangeCapability.serialize_element, element=Notice)
    async def notice(self, element: Notice) -> LgrAt:
        uin = int(element.target['member'])
        db: LagrangeDatabase = self.protocol.service.database
        return LgrAt(uin=uin, uid=db.get_user(uin)[1], text=f"{element.display or ''}")

    @m.entity(LagrangeCapability.serialize_element, element=NoticeAll)
    async def notice_all(self, element: NoticeAll) -> LgrAtAll:
        return LgrAtAll(text=TEXT_AT_ALL)

    @m.entity(LagrangeCapability.serialize_element, element=Reference)
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
            text=f'[quote:{record.msg}]',
            seq=record.seq,
            uid=db.get_user(record.friend_uin)[1],
            uin=record.friend_uin,
            timestamp=record.time,
            msg=record.msg
        )

    # @m.entity(LagrangeCapability.serialize_element, element=Dice)
    # async def dice(self, element: Dice) -> ...:
    #     return ...

    # TODO: dice, music_share, gift

    @m.entity(LagrangeCapability.serialize_element, element=Poke)
    async def poke(self, element: Poke) -> LgrPoke:
        return LgrPoke(text='[poke:1]', id=1)  # shake

    @m.entity(LagrangeCapability.serialize_element, element=Json)
    async def json(self, element: Json) -> LgrJson:
        code = element.content.encode()
        return LgrJson(text=f'[json:{len(code)}]', raw=code)

    @m.entity(LagrangeCapability.serialize_element, element=Xml)
    async def xml(self, element: Xml) -> LgrRaw:  # TODO: sure (xml)?
        code = element.content.encode()
        return LgrRaw(text=f'[raw:{len(code)}]', data=code)

    @m.entity(LagrangeCapability.serialize_element, element=App)
    async def app(self, element: App | Json) -> LgrJson:
        return await self.json(element)

    # TODO: share

    @m.entity(LagrangeCapability.serialize_element, element=MarketFace)
    async def market_face(self, element: MarketFace) -> LgrMarketFace:
        tab_id = getattr(element, 'tab_id', MarketFaceEx.tab_id)
        width = getattr(element, 'width', MarketFaceEx.width)
        height = getattr(element, 'height', MarketFaceEx.height)
        return LgrMarketFace(
            text=element.name or '[]',
            face_id=bytes.fromhex(element.id),
            tab_id=tab_id,
            width=width,
            height=height
        )
