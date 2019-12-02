import pkg_resources
import sys
import warnings

if (3, 5) <= sys.version_info < (3, 6):
    warnings.warn(
        "Support for Python 3.5 will be removed in web3.py v5",
        category=DeprecationWarning,
        stacklevel=2)

if sys.version_info < (3, 5):
    raise EnvironmentError(
        "Python 3.5 or above is required. "
        "Note that support for Python 3.5 will be removed in web3.py v5")

from vns_account import Account  # noqa: E402
from web3.main import web3  # noqa: E402
from web3.providers.rpc import (  # noqa: E402
    HTTPProvider,
)
from web3.providers.vns_tester import (  # noqa: E402
    EthereumTesterProvider,
)
from web3.providers.ipc import (  # noqa: E402
    IPCProvider,
)
from web3.providers.websocket import (  # noqa: E402
    WebsocketProvider,
)

__version__ = pkg_resources.get_distribution("web3").version

__all__ = [
    "__version__",
    "web3",
    "HTTPProvider",
    "IPCProvider",
    "WebsocketProvider",
    "TestRPCProvider",
    "EthereumTesterProvider",
    "Account",
]
