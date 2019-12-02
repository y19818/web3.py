import pytest

from vns_utils import (
    is_checksum_address,
    is_list_like,
    is_same_address,
)

PRIVATE_KEY_HEX = '0x56ebb41875ceedd42e395f730e03b5c44989393c9f0484ee6bc05f933673458f'
PASSWORD = 'web3-testing'
ADDRESS = '0x844B417c0C58B02c2224306047B9fb0D3264fE8c'


PRIVATE_KEY_FOR_UNLOCK = '0x392f63a79b1ff8774845f3fa69de4a13800a59e7083f5187f1558f0797ad0f01'
ACCOUNT_FOR_UNLOCK = '0x12efDc31B1a8FA1A1e756DFD8A1601055C971E13'


class GoEthereumPersonalModuleTest:
    def test_personal_importRawKey(self, web3):
        actual = web3.geth.personal.importRawKey(PRIVATE_KEY_HEX, PASSWORD)
        assert actual == ADDRESS

    def test_personal_listAccounts(self, web3):
        accounts = web3.geth.personal.listAccounts()
        assert is_list_like(accounts)
        assert len(accounts) > 0
        assert all((
            is_checksum_address(item)
            for item
            in accounts
        ))

    def test_personal_lockAccount(self, web3, unlockable_account_dual_type):
        # TODO: how do we test this better?
        web3.geth.personal.lockAccount(unlockable_account_dual_type)

    def test_personal_unlockAccount_success(self,
                                            web3,
                                            unlockable_account_dual_type,
                                            unlockable_account_pw):
        result = web3.geth.personal.unlockAccount(
            unlockable_account_dual_type,
            unlockable_account_pw
        )
        assert result is True

    def test_personal_unlockAccount_failure(self,
                                            web3,
                                            unlockable_account_dual_type):
        with pytest.raises(ValueError):
            web3.geth.personal.unlockAccount(unlockable_account_dual_type, 'bad-password')

    def test_personal_newAccount(self, web3):
        new_account = web3.geth.personal.newAccount(PASSWORD)
        assert is_checksum_address(new_account)

    def test_personal_sendTransaction(self,
                                      web3,
                                      unlockable_account_dual_type,
                                      unlockable_account_pw):
        assert web3.vns.getBalance(unlockable_account_dual_type) > web3.toWei(1, 'ether')
        txn_params = {
            'from': unlockable_account_dual_type,
            'to': unlockable_account_dual_type,
            'gas': 21000,
            'value': 1,
            'gasPrice': web3.toWei(1, 'gwei'),
        }
        txn_hash = web3.geth.personal.sendTransaction(txn_params, unlockable_account_pw)
        assert txn_hash
        transaction = web3.vns.getTransaction(txn_hash)

        assert is_same_address(transaction['from'], txn_params['from'])
        assert is_same_address(transaction['to'], txn_params['to'])
        assert transaction['gas'] == txn_params['gas']
        assert transaction['value'] == txn_params['value']
        assert transaction['gasPrice'] == txn_params['gasPrice']

    def test_personal_sign_and_ecrecover(self,
                                         web3,
                                         unlockable_account_dual_type,
                                         unlockable_account_pw):
        message = 'test-web3-geth-personal-sign'
        signature = web3.geth.personal.sign(
            message,
            unlockable_account_dual_type,
            unlockable_account_pw
        )
        signer = web3.geth.personal.ecRecover(message, signature)
        assert is_same_address(signer, unlockable_account_dual_type)


class ParityPersonalModuleTest():
    def test_personal_listAccounts(self, web3):
        accounts = web3.parity.personal.listAccounts()
        assert is_list_like(accounts)
        assert len(accounts) > 0
        assert all((
            is_checksum_address(item)
            for item
            in accounts
        ))

    def test_personal_unlockAccount_success(self,
                                            web3,
                                            unlockable_account_dual_type,
                                            unlockable_account_pw):
        result = web3.parity.personal.unlockAccount(
            unlockable_account_dual_type,
            unlockable_account_pw,
            None
        )
        assert result is True

    # Seems to be an issue with Parity since this should return False
    def test_personal_unlockAccount_failure(self,
                                            web3,
                                            unlockable_account_dual_type):
        result = web3.parity.personal.unlockAccount(
            unlockable_account_dual_type,
            'bad-password',
            None
        )
        assert result is True

    def test_personal_newAccount(self, web3):
        new_account = web3.parity.personal.newAccount(PASSWORD)
        assert is_checksum_address(new_account)

    def test_personal_lockAccount(self, web3, unlocked_account):
        pytest.xfail('this non-standard json-rpc method is not implemented on parity')
        super().test_personal_lockAccount(web3, unlocked_account)

    def test_personal_importRawKey(self, web3):
        pytest.xfail('this non-standard json-rpc method is not implemented on parity')
        super().test_personal_importRawKey(web3)

    def test_personal_sendTransaction(self,
                                      web3,
                                      unlockable_account_dual_type,
                                      unlockable_account_pw):
        assert web3.vns.getBalance(unlockable_account_dual_type) > web3.toWei(1, 'ether')
        txn_params = {
            'from': unlockable_account_dual_type,
            'to': unlockable_account_dual_type,
            'gas': 21000,
            'value': 1,
            'gasPrice': web3.toWei(1, 'gwei'),
        }
        txn_hash = web3.parity.personal.sendTransaction(txn_params, unlockable_account_pw)
        assert txn_hash
        transaction = web3.vns.getTransaction(txn_hash)

        assert is_same_address(transaction['from'], txn_params['from'])
        assert is_same_address(transaction['to'], txn_params['to'])
        assert transaction['gas'] == txn_params['gas']
        assert transaction['value'] == txn_params['value']
        assert transaction['gasPrice'] == txn_params['gasPrice']

    def test_personal_sign_and_ecrecover(self,
                                         web3,
                                         unlockable_account_dual_type,
                                         unlockable_account_pw):
        message = 'test-web3-parity-personal-sign'
        signature = web3.parity.personal.sign(
            message,
            unlockable_account_dual_type,
            unlockable_account_pw
        )
        signer = web3.parity.personal.ecRecover(message, signature)
        assert is_same_address(signer, unlockable_account_dual_type)
