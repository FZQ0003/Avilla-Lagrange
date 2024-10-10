import os

from avilla.core import Avilla, Context, MessageReceived
from lagrange import Client as LgrClient
from lagrange.client.events import BaseEvent
from loguru import logger

from avilla.lagrange.const import SIGN_URL
from avilla.lagrange.protocol import LagrangeConfig, LagrangeGlobalConfig, LagrangeProtocol

avilla = Avilla()


# The sign url provided here may be outdated.
# View https://github.com/LagrangeDev/Lagrange.Core to get recent one.
config = LagrangeConfig(
    int(os.getenv('LAGRANGE_UIN', '0')),
    sign_url=os.getenv('LAGRANGE_SIGN_URL', SIGN_URL)
)
global_config = LagrangeGlobalConfig('demo-database.db')
avilla.apply_protocols(LagrangeProtocol(global_config).configure(config))


# Note: raw event & client from lagrange-python can be collected here.
@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived,
                              raw_event: BaseEvent, raw_client: LgrClient):
    logger.debug(f'Raw: [{raw_client.uin}] -> {raw_event}')
    print(Avilla.current())
    await ctx.scene.send_message('Hello, Avilla!', reply=event.message)

avilla.launch()
