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
)
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
from ..base import LagrangePerform
from ...capability import LagrangeCapability
from ...resource import LagrangeResource


class LagrangeMessageDeserializePerform(LagrangePerform):

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrText)
    async def text(self, raw_element: LgrText) -> Text:
        return Text(raw_element.text)

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrEmoji)
    async def face(self, raw_element: LgrEmoji) -> Face:
        return Face(str(raw_element.id))

    # TODO: resource

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrImage)
    async def image(self, raw_element: LgrImage) -> Picture:  # TODO: FlashImage?
        return Picture(LagrangeResource(raw_element, raw_element.url))

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrAudio)
    async def record(self, raw_element: LgrAudio) -> Audio:
        return Audio(LagrangeResource(raw_element, raw_element.file_key))

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrVideo)
    async def video(self, raw_element: LgrVideo) -> Video:
        return Video(LagrangeResource(raw_element, raw_element.file_key))

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrAt)
    async def at(self, raw_element: LgrAt) -> Notice:
        scene = self.context.scene if self.context else Selector().land('qq')
        return Notice(scene.member(str(raw_element.uin)), raw_element.text)

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrAtAll)
    async def at_all(self, raw_element: LgrAtAll) -> NoticeAll:
        return NoticeAll()

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrQuote)
    async def reply(self, raw_element: LgrQuote) -> Reference:
        scene = self.context.scene if self.context else Selector().land('qq')
        return Reference(scene.message(str(raw_element.seq)))

    # @LagrangeCapability.deserialize_element.collect(...)
    # async def dice(self, raw_element: ...) -> Dice:
    #     return Dice()

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrPoke)
    async def poke(self, raw_element: LgrPoke) -> Poke:
        return Poke()  # TODO: type

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrJson)
    async def json(self, raw_element: LgrJson) -> Json:
        return Json(raw_element.raw.decode())

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrRaw)
    async def xml(self, raw_element: LgrRaw) -> Xml:  # TODO: sure (xml)?
        return Xml(raw_element.data.decode())

    # @LagrangeCapability.deserialize_element.collect(...)
    # async def share(self, raw_element: ...) -> Share:
    #     return Share(
    #         url=...,
    #         title=...,
    #         content=...,
    #         thumbnail=...,
    #     )

    # TODO: forward, file, GreyTips

    @LagrangeCapability.deserialize_element.collect(raw_element=LgrMarketFace)
    async def market_face(self, raw_element: LgrMarketFace) -> MarketFaceEx:
        return MarketFaceEx(
            id=raw_element.face_id.hex(),
            tab_id=raw_element.tab_id,
            width=raw_element.width,
            height=raw_element.height,
            name=raw_element.text
        )
