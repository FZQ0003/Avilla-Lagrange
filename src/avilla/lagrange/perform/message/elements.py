from dataclasses import dataclass

from avilla.standard.qq.elements import MarketFace


@dataclass
class MarketFaceEx(MarketFace):
    tab_id: int = 0
    width: int = 200
    height: int = 200
