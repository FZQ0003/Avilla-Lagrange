# import json
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from avilla.core import Selector
from avilla.core.account import AccountInfo
from avilla.core.ryanvk.staff import Staff
from lagrange import Client
from lagrange.info.app import app_list
from lagrange.utils.sign import sign_provider
from launart import Service, Launart, any_completed
from launart.status import Phase
from loguru import logger

from .account import LagrangeAccount
from .capability import LagrangeCapability
from .const import PLATFORM
from .types import Event, AVAILABLE_EVENTS

if TYPE_CHECKING:
    from .protocol import LagrangeProtocol, LagrangeConfig


class LagrangeClientService(Service):
    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[Phase]:
        return {'preparing', 'blocking', 'cleanup'}

    account: LagrangeAccount
    client: Client
    config: 'LagrangeConfig'
    protocol: 'LagrangeProtocol'

    def __init__(self, protocol: 'LagrangeProtocol', config: 'LagrangeConfig'):
        super().__init__()
        self.protocol = protocol
        # config <=> client <=> account
        self.config = config
        self.client = Client(
            config.uin,
            app_list[config.protocol],
            config.device_info,
            config.sign_info,
            sign_provider(config.sign_url) if config.sign_url else None
        )

    @property
    def id(self):
        return f'lagrange/connection/client#{self.client.uin}'

    def init_account(self) -> LagrangeAccount:
        if hasattr(self, 'account'):
            return self.account
        route: Selector = Selector().land('qq').account(str(self.client.uin))
        account = LagrangeAccount(route=route, protocol=self.protocol)
        self.account = account
        # Add to avilla
        self.protocol.avilla.accounts[route] = AccountInfo(
            route=route,
            account=account,
            protocol=self.protocol,
            platform=PLATFORM
        )
        # account.uid_map = config.cache.get('uid_map', {0: {}})
        return account

    async def login(self) -> bool:
        # Use LagrangeEventLifespanPerform.online() to enable self.account.status
        if self.config.sign_info.d2:
            if not await self.client.register():
                return await self.client.login()
            return True
        else:
            return await self.client.login()

    async def update_uid_map(self, from_friends: bool = True, from_members: bool = True) -> dict[int, str]:
        if self.account.available:
            if from_members:
                rsp_g = await self.client.get_grp_list()
                for group in rsp_g.grp_list:
                    has_next, next_key = True, None
                    while has_next:
                        rsp_m = await self.client.get_grp_members(group.grp_id, next_key)
                        for member in rsp_m.body:
                            if uin := member.account.uin:  # uin is optional
                                self.account.uid_map[uin] = member.account.uid
                        next_key = rsp_m.next_key
                        has_next = next_key is not None
            if from_friends:
                rsp_f = await self.client.get_friend_list()
                for friend in rsp_f:
                    if uid := friend.uid:  # uid is optional (...)
                        self.account.uid_map[friend.uin] = uid
        return self.account.uid_map

    def get_staff_components(self):
        return {'connection': self, 'protocol': self.protocol, 'avilla': self.protocol.avilla}

    def get_staff_artifacts(self):
        return [self.protocol.artifacts, self.protocol.avilla.global_artifacts]

    @property
    def staff(self):
        return Staff(self.get_staff_artifacts(), self.get_staff_components())

    async def launch(self, manager: Launart):
        async with self.stage('preparing'):
            self.init_account()

            # client is unused for there is a self.client
            async def handler(client: Client, event: Event):  # noqa
                # cache uid (always update)
                if hasattr(event, 'grp_id') and hasattr(event, 'uin') and hasattr(event, 'uid'):
                    # if event.grp_id not in self.account.uid_map:
                    #     self.account.uid_map[event.grp_id] = {0: str(event.grp_id)}
                    # self.account.uid_map[event.grp_id][event.uin] = event.uid
                    self.account.uid_map[event.uin] = event.uid
                if hasattr(event, 'from_uin') and hasattr(event, 'from_uid'):
                    # self.account.uid_map[0][event.from_uin] = event.from_uid
                    self.account.uid_map[event.from_uin] = event.from_uid
                if hasattr(event, 'to_uin') and hasattr(event, 'to_uid'):
                    # self.account.uid_map[0][event.to_uin] = event.to_uid
                    self.account.uid_map[event.to_uin] = event.to_uid
                # handle event
                with suppress(NotImplementedError):
                    await LagrangeCapability(self.staff).handle_event(event)
                    return
                logger.warning(f'Client {client.uin} received unsupported event: {event.__class__.__name__}')

            # lagrange.subscribe
            for event in AVAILABLE_EVENTS:
                self.client.events.subscribe(event, handler)
            self.client.connect()
            # lagrange.login
            if not await self.login():
                return
            await self.update_uid_map()
            # lagrange.im.save_all
            if not Path(self.config.device_info_path).is_dir():
                with open(self.config.device_info_path, 'wb') as f:
                    f.write(self.config.device_info.dump())
            if not Path(self.config.sign_info_path).is_dir():
                with open(self.config.sign_info_path, 'wb') as f:
                    f.write(self.config.sign_info.dump())

        async with self.stage('blocking'):
            # lagrange.run
            await any_completed(
                manager.status.wait_for_sigexit(),
                self.client.wait_closed()
            )

        async with self.stage('cleanup'):
            # await self.client.stop()
            # save cache
            # self.config.cache['uid_map'] = self.account
            # if not Path(self.config.cache_path).is_dir():
            #     with open(self.config.cache_path, 'w') as f:
            #         json.dump(self.config.cache, f)
            ...
