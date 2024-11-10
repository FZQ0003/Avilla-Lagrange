from avilla.core import Land, Platform, Abstract, Selector

# From Lagrange.Core
SIGN_URL = 'https://sign.lagrangecore.org/api/sign/25765'

# From lagrange-python
SIGN_SEQ = 8848

# MessageChain
TEXT_AT_ALL = '@全体成员'

# From avilla
LAND = Land('qq', [{'name': 'Tencent'}], humanized_name='QQ')
PLATFORM = Platform(
    LAND,
    Abstract(
        protocol='lagrange-python',
        maintainers=[{'name': 'LagrangeDev'}],
        humanized_name='Lagrange-python Protocol',
    ),
    Land(
        'lagrange',
        [{'name': 'GraiaProject'}, {'name': 'F_Qilin'}],
        humanized_name='Lagrange-python for Avilla',
    ),
)
LAND_SELECTOR = Selector().land(LAND)
