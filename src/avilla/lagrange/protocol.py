import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from avilla.core import Avilla
from avilla.core.protocol import ProtocolConfig, BaseProtocol
from graia.ryanvk import merge, ref
from lagrange.info import DeviceInfo, SigInfo

from .client import LagrangeClientService
from .const import SIGN_SEQ, SIGN_URL
from .service import LagrangeService
from .utils.broadcast import AvillaLagrangeStopDispatcher


@dataclass
class LagrangeGlobalConfig(ProtocolConfig):
    database_path: os.PathLike[str] | str = ':memory:'


@dataclass
class LagrangeConfig(ProtocolConfig):
    uin: int
    protocol: Literal['linux', 'macos', 'windows'] = 'linux'
    sign_url: str = SIGN_URL
    device_info_path: os.PathLike[str] | str = './device.json'
    sign_info_path: os.PathLike[str] | str = './sig.bin'
    device_info: DeviceInfo | None = None
    sign_info: SigInfo | None = None
    allow_self_msg: bool = False

    def __post_init__(self):
        # Check if info is pre-defined (use temp path instead)
        if self.device_info:
            self.device_info_path = ''
        if self.sign_info:
            self.sign_info_path = ''
    
    def read_info(self, force: bool = False) -> tuple[DeviceInfo, SigInfo]:
        if self.device_info and not force:
            ...
        elif Path(self.device_info_path).is_file():
            with open(self.device_info_path, 'rb') as f:
                self.device_info = DeviceInfo.load(f.read())
        else:
            self.device_info = DeviceInfo.generate(self.uin)
        if self.sign_info and not force:
            ...
        elif self.sign_info:
            self.sign_info = self.sign_info
        elif Path(self.sign_info_path).is_file():
            with open(self.sign_info_path, 'rb') as f:
                self.sign_info = SigInfo.load(f.read())
        else:
            self.sign_info = SigInfo.new(SIGN_SEQ)
        return self.device_info, self.sign_info
    
    def save_info(self) -> None:
        if self.device_info and not Path(self.device_info_path).is_dir():
            with open(self.device_info_path, 'wb') as f:
                f.write(self.device_info.dump())
        if self.sign_info and not Path(self.sign_info_path).is_dir():
            with open(self.sign_info_path, 'wb') as f:
                f.write(self.sign_info.dump())


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

    def __init__(self, config: LagrangeGlobalConfig = LagrangeGlobalConfig()):
        self.service = LagrangeService(self, config)

    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        avilla.launch_manager.add_component(self.service)
        avilla.broadcast.finale_dispatchers.append(AvillaLagrangeStopDispatcher())

    def configure(self, config: ProtocolConfig):
        if not isinstance(config, LagrangeConfig):
            raise ValueError('Invalid config')
        # int for keys, not str
        self.service.service_map[int(config.uin)] = LagrangeClientService(self, config)
        return self
