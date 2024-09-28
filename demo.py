import os

from avilla.core import Avilla, Context, MessageReceived

from avilla.lagrange.protocol import LagrangeConfig, LagrangeGlobalConfig, LagrangeProtocol

avilla = Avilla()


# View https://github.com/LagrangeDev/Lagrange.Core to get recent sign url.
config = LagrangeConfig(
    int(os.getenv('LAGRANGE_UIN', '0')),
    sign_url=os.getenv('LAGRANGE_SIGN_URL', '')
)
global_config = LagrangeGlobalConfig('demo-database.db')
avilla.apply_protocols(LagrangeProtocol(global_config).configure(config))


@avilla.listen(MessageReceived)
async def on_message_received(ctx: Context, event: MessageReceived):
    await ctx.scene.send_message('Hello, Avilla!', reply=event.message)

avilla.launch()
