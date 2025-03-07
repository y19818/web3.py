import pytest

from web3 import Web3
from web3.exceptions import (
    InvalidAddress,
)
from web3.middleware import (  # noqa: F401
    construct_fixture_middleware,
    name_to_address_middleware,
)
from web3.providers.base import (
    BaseProvider,
)

NAME = "dump.vns"
ADDRESS = "0x0000000000000000000000000000000000000000"
BALANCE = 0


class TempENS():
    def __init__(self, name_addr_pairs):
        self.registry = dict(name_addr_pairs)

    def address(self, name):
        return self.registry.get(name, None)


@pytest.fixture
def w3():
    w3 = Web3(provider=BaseProvider(), middlewares=[])
    w3.ens = TempENS({NAME: ADDRESS})
    w3.middleware_onion.add(name_to_address_middleware(w3))
    return w3


def test_pass_name_resolver(w3):
    return_chain_on_mainnet = construct_fixture_middleware({
        'net_version': '1',
    })
    return_balance = construct_fixture_middleware({
        'vns_getBalance': BALANCE
    })
    w3.middleware_onion.inject(return_chain_on_mainnet, layer=0)
    w3.middleware_onion.inject(return_balance, layer=0)
    assert w3.vns.getBalance(NAME) == BALANCE


def test_fail_name_resolver(w3):
    return_chain_on_mainnet = construct_fixture_middleware({
        'net_version': '2',
    })
    w3.middleware_onion.inject(return_chain_on_mainnet, layer=0)
    with pytest.raises(InvalidAddress, match=r'.*ethereum\.vns.*'):
        w3.vns.getBalance("ethereum.vns")
