# import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from avilla.core import Avilla
from avilla.core.protocol import ProtocolConfig, BaseProtocol
from graia.ryanvk import merge, ref
from lagrange.info import DeviceInfo, SigInfo

from .connection import LagrangeClientService
from .const import SIGN_SEQ
from .service import LagrangeService


@dataclass
class LagrangeConfig(ProtocolConfig):
    uin: int
    protocol: Literal['linux', 'macos', 'windows'] = 'linux'
    sign_url: str = ''
    device_info_path: os.PathLike | str = './device.json'
    sign_info_path: os.PathLike | str = './sig.bin'
    # cache_path: os.PathLike | str = './cache.json'
    device_info: DeviceInfo = None
    sign_info: SigInfo = None
    # cache: dict = None

    def __post_init__(self):
        # Check if info is pre-defined (use temp path instead)
        # device info
        if isinstance(self.device_info, DeviceInfo):
            self.device_info_path = ''
        elif Path(self.device_info_path).is_file():
            with open(self.device_info_path, 'rb') as f:
                self.device_info = DeviceInfo.load(f.read())
        else:
            self.device_info = DeviceInfo.generate(self.uin)
        # sign info
        if isinstance(self.sign_info, SigInfo):
            self.sign_info_path = ''
        elif Path(self.sign_info_path).is_file():
            with open(self.sign_info_path, 'rb') as f:
                self.sign_info = SigInfo.load(f.read())
        else:
            self.sign_info = SigInfo.new(SIGN_SEQ)
        # TODO: cache
        # if isinstance(self.cache, dict):
        #     self.cache_path = ''
        # elif Path(self.cache_path).is_file():
        #     with open(self.cache_path, 'r') as f:
        #         self.cache = json.load(f)
        # else:
        #     self.cache = {}


def _import_performs():
    from . import logger  # noqa: F401
    from .perform import context  # noqa: F401
    from .perform.action import message  # noqa: F401
    from .perform.event import lifespan, message  # noqa: F401
    from .perform.message import deserialize, serialize  # noqa: F401


class LagrangeProtocol(BaseProtocol):
    service: LagrangeService

    _import_performs()
    artifacts = {
        **merge(
            ref('avilla.protocol/lagrange::action', 'message'),
            ref('avilla.protocol/lagrange::event', 'lifespan'),
            ref('avilla.protocol/lagrange::event', 'message'),
            ref('avilla.protocol/lagrange::message', 'deserialize'),
            ref('avilla.protocol/lagrange::message', 'serialize'),
            ref('avilla.protocol/lagrange::context'),
        )
    }

    def __init__(self):
        self.service = LagrangeService(self)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        avilla.launch_manager.add_component(self.service)

    def configure(self, config: LagrangeConfig):
        # int for keys, not str
        self.service.connection_map[int(config.uin)] = LagrangeClientService(self, config)
        return self
