import pytest

from flaky import (
    flaky,
)

from web3._utils.module_testing import (  # noqa: F401
    EthModuleTest,
    ParityModuleTest as TraceModuleTest,
    ParityPersonalModuleTest,
    Web3ModuleTest,
)
from web3._utils.module_testing.vns_module import (
    UNKNOWN_ADDRESS,
)
from web3._utils.module_testing.shh_module import (
    ParityShhModuleTest,
)

# some tests appear flaky with Parity v1.10.x
MAX_FLAKY_RUNS = 3


class ParityWeb3ModuleTest (Web3ModuleTest):
    def _check_web3_clientVersion(self, client_version):
        assert client_version.startswith('Parity-Ethereum/')


class ParityEthModuleTest(EthModuleTest):
    def test_vns_chainId(self, web3):
        # Parity will return null if chainId is not available
        chain_id = web3.vns.chainId
        assert chain_id is None

    def test_vns_getBlockByNumber_pending(self, web3):
        pytest.xfail('Parity dropped "pending" option in 1.11.1')
        super().test_vns_getBlockByNumber_pending(web3)

    def test_vns_uninstallFilter(self, web3):
        pytest.xfail('vns_uninstallFilter calls to parity always return true')
        super().test_vns_uninstallFilter(web3)

    def test_vns_replaceTransaction(self, web3, unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction(web3, unlocked_account)

    def test_vns_replaceTransaction_already_mined(self, web3, unlocked_account):
        pytest.xfail('Parity is not setup to auto mine')
        super().test_vns_replaceTransaction_already_mined(web3, unlocked_account)

    def test_vns_replaceTransaction_incorrect_nonce(self, web3, unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction_incorrect_nonce(web3, unlocked_account)

    def test_vns_replaceTransaction_gas_price_too_low(self, web3, unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction_gas_price_too_low(web3, unlocked_account)

    def test_vns_replaceTransaction_gas_price_defaulting_minimum(self, web3, unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction_gas_price_defaulting_minimum(web3, unlocked_account)

    def test_vns_replaceTransaction_gas_price_defaulting_strategy_higher(self,
                                                                         web3,
                                                                         unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction_gas_price_defaulting_strategy_higher(
            web3, unlocked_account
        )

    def test_vns_replaceTransaction_gas_price_defaulting_strategy_lower(self,
                                                                        web3,
                                                                        unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction_gas_price_defaulting_strategy_lower(
            web3, unlocked_account
        )

    def test_vns_modifyTransaction(self, web3, unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_modifyTransaction(web3, unlocked_account)

    @flaky(max_runs=MAX_FLAKY_RUNS)
    def test_vns_getTransactionReceipt_unmined(self, web3, unlocked_account):
        # Parity diverges from json-rpc spec and retrieves pending block
        # transactions with getTransactionReceipt.
        txn_hash = web3.vns.sendTransaction({
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        })
        receipt = web3.vns.getTransactionReceipt(txn_hash)
        assert receipt is not None
        assert receipt['blockHash'] is None

    def test_vns_getLogs_with_logs_none_topic_args(self, web3):
        pytest.xfail("Parity matches None to asbent values")
        super().test_vns_getLogs_with_logs_none_topic_args(web3)

    @flaky(max_runs=MAX_FLAKY_RUNS)
    def test_vns_call_old_contract_state(self, web3, math_contract, unlocked_account):
        start_block = web3.vns.getBlock('latest')
        block_num = start_block.number
        block_hash = start_block.hash

        math_contract.functions.increment().transact({'from': unlocked_account})

        # This isn't an incredibly convincing test since we can't mine, and
        # the default resolved block is latest, So if block_identifier was ignored
        # we would get the same result. For now, we mostly depend on core tests.
        # Ideas to improve this test:
        #  - Enable on-demand mining in more clients
        #  - Increment the math contract in all of the fixtures, and check the value in an old block

        block_hash_call_result = math_contract.functions.counter().call(block_identifier=block_hash)
        block_num_call_result = math_contract.functions.counter().call(block_identifier=block_num)
        latest_call_result = math_contract.functions.counter().call(block_identifier='latest')
        default_call_result = math_contract.functions.counter().call()

        assert block_hash_call_result == 0
        assert block_num_call_result == 0
        assert latest_call_result == 0
        assert default_call_result == 0

        # retrieve this right before using - Parity tests might hit a race otherwise
        pending_call_result = math_contract.functions.counter().call(block_identifier='pending')
        # should be '1' on first flaky run, '2' on second, or '3' on third
        if pending_call_result not in range(1, MAX_FLAKY_RUNS + 1):
            raise AssertionError("pending call result was %d!" % pending_call_result)

    def test_vns_getLogs_without_logs(self, web3, block_with_txn_with_log):
        # Test with block range

        filter_params = {
            "fromBlock": 0,
            "toBlock": block_with_txn_with_log['number'] - 1,
        }
        result = web3.vns.getLogs(filter_params)
        assert len(result) == 0

        # the range is wrong, parity returns error message
        filter_params = {
            "fromBlock": block_with_txn_with_log['number'],
            "toBlock": block_with_txn_with_log['number'] - 1,
        }
        with pytest.raises(ValueError):
            web3.vns.getLogs(filter_params)

        # Test with `address`

        # filter with other address
        filter_params = {
            "fromBlock": 0,
            "address": UNKNOWN_ADDRESS,
        }
        result = web3.vns.getLogs(filter_params)
        assert len(result) == 0

        # Test with multiple `address`

        # filter with other address
        filter_params = {
            "fromBlock": 0,
            "address": [UNKNOWN_ADDRESS, UNKNOWN_ADDRESS],
        }
        result = web3.vns.getLogs(filter_params)
        assert len(result) == 0


class ParityTraceModuleTest(TraceModuleTest):
    pass


class CommonParityShhModuleTest(ParityShhModuleTest):
    def test_shh_sync_filter(self, web3):
        # https://github.com/paritytech/parity-ethereum/issues/10565
        pytest.xfail("Skip until parity filter bug is resolved")
        super().test_shh_sync_filter(web3)

    def test_shh_async_filter(self, web3):
        # https://github.com/paritytech/parity-ethereum/issues/10565
        pytest.xfail("Skip until parity filter bug is resolved")
        super().test_shh_async_filter(web3)
