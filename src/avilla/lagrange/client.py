from typing import TYPE_CHECKING

from avilla.core import Selector
from avilla.core.account import AccountInfo
from lagrange import Client
from lagrange.info.app import app_list
from lagrange.utils.sign import sign_provider
from launart import Service, Launart, any_completed
from launart.status import Phase

from .account import LagrangeAccount
from .capability import LagrangeCapability
from .const import LAND, PLATFORM
from .types import AVAILABLE_EVENTS

if TYPE_CHECKING:
    from .protocol import LagrangeProtocol, LagrangeConfig


class LagrangeClientService(Service):
    account: LagrangeAccount
    client: Client
    config: 'LagrangeConfig'
    protocol: 'LagrangeProtocol'

    def __init__(self, protocol: 'LagrangeProtocol', config: 'LagrangeConfig'):
        super().__init__()
        self.protocol = protocol
        # config <=> client <=> account
        info = config.read_info()
        self.config = config
        self.client = Client(
            config.uin,
            app_list[config.protocol],
            info[0],
            info[1],
            sign_provider(config.sign_url) if config.sign_url else None
        )
        self.id = f'lagrange/client#{config.uin}'

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[Phase]:
        return {'preparing', 'blocking', 'cleanup'}

    def init_account(self) -> LagrangeAccount:
        if hasattr(self, 'account'):
            return self.account
        route: Selector = Selector().land(LAND.name).account(str(self.client.uin))
        account = LagrangeAccount(route=route, avilla=self.protocol.avilla)
        self.account = account
        # Add to avilla
        self.protocol.avilla.accounts[route] = AccountInfo(
            route=route,
            account=account,
            protocol=self.protocol,
            platform=PLATFORM
        )
        return account

    async def login(self) -> bool:
        # Use LagrangeEventLifespanPerform.online() to enable self.account.status
        if self.config.sig_info and self.config.sig_info.d2:
            if not await self.client.register():
                return await self.client.login()
            return True
        else:
            return await self.client.login()

    async def update_user_db(self, from_friends: bool = True, from_members: bool = True) -> None:
        if not self.account.available:
            return
        db = self.protocol.service.database
        if from_members:
            rsp_g = await self.client.get_grp_list()
            for group in rsp_g.grp_list:
                has_next, next_key = True, None
                while has_next:
                    rsp_m = await self.client.get_grp_members(group.grp_id, next_key)
                    for member in rsp_m.body:
                        if uin := member.account.uin:  # uin is optional
                            db.insert_user(uin, member.account.uid)
                    next_key = rsp_m.next_key.decode() if rsp_m.next_key else None
                    has_next = next_key is not None
        if from_friends:
            rsp_f = await self.client.get_friend_list()
            for friend in rsp_f:
                if uid := friend.uid:  # uid is optional (...)
                    db.insert_user(friend.uin, uid)

    async def launch(self, manager: Launart):
        async with self.stage('preparing'):
            # Init account
            capability = LagrangeCapability(self.protocol, self.init_account())
            # lagrange.subscribe
            for a_event in AVAILABLE_EVENTS:
                self.client.events.subscribe(a_event, capability.handle_event)
            self.client.connect()
            # lagrange.login
            if not await self.login():
                return
            await self.update_user_db()
            # lagrange.im.save_all
            self.config.save_info()

        async with self.stage('blocking'):
            # lagrange.run
            await any_completed(
                manager.status.wait_for_sigexit(),
                self.client.wait_closed()
            )

        async with self.stage('cleanup'):
            await self.client.stop()
