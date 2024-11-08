import os

from lagrange import Lagrange, install_loguru

from avilla.lagrange.const import SIGN_URL

lag = Lagrange(
    int(os.environ.get('LAGRANGE_UIN', '0')),
    'linux',
    os.environ.get('LAGRANGE_SIGN_URL', SIGN_URL)
)
install_loguru()
lag.log.set_level('DEBUG')

lag.launch()
