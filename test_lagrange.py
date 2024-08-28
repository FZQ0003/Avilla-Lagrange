import os

from lagrange import Lagrange, install_loguru

lag = Lagrange(
    int(os.environ.get('LAGRANGE_UIN', '0')),
    'linux',
    os.environ.get('LAGRANGE_SIGN_URL', '')
)
install_loguru()
lag.log.set_level('DEBUG')

lag.launch()
