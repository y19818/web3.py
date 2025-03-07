import random

from vns_utils import (
    decode_hex,
)
from flaky import (
    flaky,
)

from web3._utils.threads import (
    Timeout,
)


@flaky(max_runs=3)
def test_miner_setExtra(web3_empty, wait_for_block):
    web3 = web3_empty

    initial_extra = decode_hex(web3.vns.getBlock(web3.vns.blockNumber)['extraData'])

    new_extra_data = b'-this-is-32-bytes-of-extra-data-'

    # sanity
    assert initial_extra != new_extra_data

    web3.geth.miner.setExtra(new_extra_data)

    with Timeout(60) as timeout:
        while True:
            extra_data = decode_hex(web3.vns.getBlock(web3.vns.blockNumber)['extraData'])
            if extra_data == new_extra_data:
                break
            timeout.sleep(random.random())

    after_extra = decode_hex(web3.vns.getBlock(web3.vns.blockNumber)['extraData'])

    assert after_extra == new_extra_data
