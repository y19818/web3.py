import random

from flaky import (
    flaky,
)

from web3._utils.threads import (
    Timeout,
)


@flaky(max_runs=3)
def test_miner_setGasPrice(web3_empty, wait_for_block):
    web3 = web3_empty

    initial_gas_price = web3.vns.gasPrice

    # sanity check
    assert web3.vns.gasPrice > 1000

    web3.geth.miner.setGasPrice(initial_gas_price // 2)

    with Timeout(60) as timeout:
        while web3.vns.gasPrice == initial_gas_price:
            timeout.sleep(random.random())

    after_gas_price = web3.vns.gasPrice
    assert after_gas_price < initial_gas_price
