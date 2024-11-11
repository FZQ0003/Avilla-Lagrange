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
from .perform import import_performs
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
    sig_info_path: os.PathLike[str] | str = './sig.bin'
    device_info: DeviceInfo | None = None
    sig_info: SigInfo | None = None

    def __post_init__(self):
        # Check if info is pre-defined (use temp path instead)
        if self.device_info:
            self.device_info_path = ''
        if self.sig_info:
            self.sig_info_path = ''

    def read_info(self, force: bool = False) -> tuple[DeviceInfo, SigInfo]:
        if self.device_info and not force:
            ...
        elif Path(self.device_info_path).is_file():
            with open(self.device_info_path, 'rb') as f:
                self.device_info = DeviceInfo.load(f.read())
        else:
            self.device_info = DeviceInfo.generate(self.uin)
        if self.sig_info and not force:
            ...
        elif self.sig_info:
            self.sig_info = self.sig_info
        elif Path(self.sig_info_path).is_file():
            with open(self.sig_info_path, 'rb') as f:
                self.sig_info = SigInfo.load(f.read())
        else:
            self.sig_info = SigInfo.new(SIGN_SEQ)
        return self.device_info, self.sig_info

    def save_info(self) -> None:
        if self.device_info and not Path(self.device_info_path).is_dir():
            with open(self.device_info_path, 'wb') as f:
                f.write(self.device_info.dump())
        if self.sig_info and not Path(self.sig_info_path).is_dir():
            with open(self.sig_info_path, 'wb') as f:
                f.write(self.sig_info.dump())


class LagrangeProtocol(BaseProtocol):
    service: LagrangeService

    from . import logger  # noqa: F401
    import_performs()
    artifacts = {**merge(ref('avilla.protocol/lagrange::compat'))}

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
