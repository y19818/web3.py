import pytest

from web3._utils.module_testing import (  # noqa: F401
    EthModuleTest,
    GoEthereumPersonalModuleTest,
    GoEthereumShhModuleTest,
    NetModuleTest,
    VersionModuleTest,
    Web3ModuleTest,
)


class GoEthereumTest (Web3ModuleTest):
    def _check_web3_clientVersion(self, client_version):
        assert client_version.startswith('Geth/')


class GoEthereumEthModuleTest(EthModuleTest):
    def test_vns_replaceTransaction(self, web3, unlocked_account):
        pytest.xfail('Needs ability to efficiently control mining')
        super().test_vns_replaceTransaction(web3, unlocked_account)

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

    def test_vns_estimateGas_with_block(self,
                                        web3,
                                        unlocked_account_dual_type):
        pytest.xfail('Block identifier has not been implemented in geth')
        super().test_vns_estimateGas_with_block(
            web3, unlocked_account_dual_type
        )

    def test_vns_submitHashrate(self, web3):
        if 'v1.8.22' in web3.clientVersion:
            # https://github.com/ethereum/go-ethereum/commit/51db5975cc5fb88db6a0dba1826b534fd4df29d7
            pytest.xfail('vns_submitHashrate deprecated in 1.8.22 for ethash_submitHashRate')
        super().test_vns_submitHashrate(web3)

    def test_vns_chainId(self, web3):
        if 'v1.7.2' in web3.clientVersion:
            pytest.xfail('vns_chainId not implemented in geth 1.7.2')
        super().test_vns_chainId(web3)


class GoEthereumVersionModuleTest(VersionModuleTest):
    pass


class GoEthereumNetModuleTest(NetModuleTest):
    pass


class CommonGoEthereumShhModuleTest(GoEthereumShhModuleTest):
    def test_shh_sync_filter(self, web3):
        if 'v1.7.2' in web3.clientVersion:
            pytest.xfail('Whisper version 6 not supported in geth 1.7.2')
        super().test_shh_sync_filter(web3)

    def test_shh_async_filter(self, web3):
        if 'v1.7.2' in web3.clientVersion:
            pytest.xfail('Whisper version 6 not supported in geth 1.7.2')
        super().test_shh_async_filter(web3)

    def test_shh_post(self, web3):
        if 'v1.7.2' in web3.clientVersion:
            pytest.xfail('Whisper version 6 not supported in geth 1.7.2')
        super().test_shh_post(web3)
