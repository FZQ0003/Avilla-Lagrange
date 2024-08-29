from __future__ import annotations

# from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.elements import (
    Audio,
    Face,
    # File,
    Notice,
    NoticeAll,
    Picture,
    Reference,
    Text,
    Video,
)
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.standard.qq.elements import (
    # Dice,
    # FlashImage,
    # Forward,
    Json,
    # Node,
    Poke,
    # Share,
    Xml,
    MarketFace,
)
from graia.ryanvk import OptionalAccess
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
)

from .elements import MarketFaceEx
from ...capability import LagrangeCapability
from ...resource import LagrangeResource

if TYPE_CHECKING:
    from avilla.core.context import Context
    from ...account import LagrangeAccount


class LagrangeMessageDeserializePerform((m := ApplicationCollector())._):
    m.namespace = 'avilla.protocol/lagrange::message'
    m.identify = 'deserialize'

    context: OptionalAccess[Context] = OptionalAccess()
    account: OptionalAccess[LagrangeAccount] = OptionalAccess()

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrText)
    async def text(self, raw_element: LgrText) -> Text:
        return Text(raw_element.text)

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrEmoji)
    async def face(self, raw_element: LgrEmoji) -> Face:
        return Face(str(raw_element.id))

    # TODO: resource

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrImage)
    async def image(self, raw_element: LgrImage) -> Picture:  # TODO: FlashImage?
        return Picture(LagrangeResource(raw_element, raw_element.url))

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrAudio)
    async def record(self, raw_element: LgrAudio) -> Audio:
        return Audio(LagrangeResource(raw_element, raw_element.file_key))

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrVideo)
    async def video(self, raw_element: LgrVideo) -> Video:
        return Video(LagrangeResource(raw_element, raw_element.file_key))

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrAt)
    async def at(self, raw_element: LgrAt) -> Notice:
        scene = self.context.scene if self.context else Selector().land('qq')
        return Notice(scene.member(str(raw_element.uin)), raw_element.text)

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrAtAll)
    async def at_all(self, raw_element: LgrAtAll) -> NoticeAll:
        return NoticeAll()

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrQuote)
    async def reply(self, raw_element: LgrQuote) -> Reference:
        scene = self.context.scene if self.context else Selector().land('qq')
        return Reference(scene.message(str(raw_element.seq)))

    # @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrText)
    # async def dice(self, raw_element: ...) -> Dice:
    #     return Dice()

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrPoke)
    async def poke(self, raw_element: LgrPoke) -> Poke:
        return Poke()

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrJson)
    async def json(self, raw_element: LgrJson) -> Json:
        return Json(raw_element.raw.decode())

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrRaw)
    async def xml(self, raw_element: LgrRaw) -> Xml:  # TODO: sure (xml)?
        return Xml(raw_element.data.decode())

    # @m.entity(LagrangeCapability.deserialize_element, raw_element=...)
    # async def share(self, raw_element: ...) -> Share:
    #     return Share(
    #         url=...,
    #         title=...,
    #         content=...,
    #         thumbnail=...,
    #     )

    # TODO: forward, file

    @m.entity(LagrangeCapability.deserialize_element, raw_element=LgrMarketFace)
    async def market_face(self, raw_element: LgrMarketFace) -> MarketFaceEx:
        return MarketFaceEx(
            id=raw_element.face_id.hex(),
            tab_id=raw_element.tab_id,
            width=raw_element.width,
            height=raw_element.height,
            name=raw_element.text
        )
