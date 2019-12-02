# -*- coding: utf-8 -*-

import pytest

from vns_abi import (
    decode_single,
)
from vns_utils import (
    is_boolean,
    is_bytes,
    is_checksum_address,
    is_dict,
    is_integer,
    is_list_like,
    is_same_address,
    is_string,
    to_int,
)
from hexbytes import (
    HexBytes,
)

from web3.exceptions import (
    BlockNotFound,
    InvalidAddress,
    TransactionNotFound,
)

UNKNOWN_ADDRESS = '0xdEADBEeF00000000000000000000000000000000'
UNKNOWN_HASH = '0xdeadbeef00000000000000000000000000000000000000000000000000000000'


class EthModuleTest:
    def test_vns_protocolVersion(self, web3):
        protocol_version = web3.vns.protocolVersion

        assert is_string(protocol_version)
        assert protocol_version.isdigit()

    def test_vns_syncing(self, web3):
        syncing = web3.vns.syncing

        assert is_boolean(syncing) or is_dict(syncing)

        if is_boolean(syncing):
            assert syncing is False
        elif is_dict(syncing):
            assert 'startingBlock' in syncing
            assert 'currentBlock' in syncing
            assert 'highestBlock' in syncing

            assert is_integer(syncing['startingBlock'])
            assert is_integer(syncing['currentBlock'])
            assert is_integer(syncing['highestBlock'])

    def test_vns_coinbase(self, web3):
        coinbase = web3.vns.coinbase
        assert is_checksum_address(coinbase)

    def test_vns_mining(self, web3):
        mining = web3.vns.mining
        assert is_boolean(mining)

    def test_vns_hashrate(self, web3):
        hashrate = web3.vns.hashrate
        assert is_integer(hashrate)
        assert hashrate >= 0

    def test_vns_chainId(self, web3):
        chain_id = web3.vns.chainId
        # chain id value from geth fixture genesis file
        assert to_int(hexstr=chain_id) == 131277322940537

    def test_vns_gasPrice(self, web3):
        gas_price = web3.vns.gasPrice
        assert is_integer(gas_price)
        assert gas_price > 0

    def test_vns_accounts(self, web3):
        accounts = web3.vns.accounts
        assert is_list_like(accounts)
        assert len(accounts) != 0
        assert all((
            is_checksum_address(account)
            for account
            in accounts
        ))
        assert web3.vns.coinbase in accounts

    def test_vns_blockNumber(self, web3):
        block_number = web3.vns.blockNumber
        assert is_integer(block_number)
        assert block_number >= 0

    def test_vns_getBalance(self, web3):
        coinbase = web3.vns.coinbase

        with pytest.raises(InvalidAddress):
            web3.vns.getBalance(coinbase.lower())

        balance = web3.vns.getBalance(coinbase)

        assert is_integer(balance)
        assert balance >= 0

    def test_vns_getStorageAt(self, web3, emitter_contract_address):
        storage = web3.vns.getStorageAt(emitter_contract_address, 0)
        assert isinstance(storage, HexBytes)

    def test_vns_getStorageAt_invalid_address(self, web3):
        coinbase = web3.vns.coinbase
        with pytest.raises(InvalidAddress):
            web3.vns.getStorageAt(coinbase.lower(), 0)

    def test_vns_getTransactionCount(self, web3, unlocked_account_dual_type):
        transaction_count = web3.vns.getTransactionCount(unlocked_account_dual_type)
        assert is_integer(transaction_count)
        assert transaction_count >= 0

    def test_vns_getTransactionCount_invalid_address(self, web3):
        coinbase = web3.vns.coinbase
        with pytest.raises(InvalidAddress):
            web3.vns.getTransactionCount(coinbase.lower())

    def test_vns_getBlockTransactionCountByHash_empty_block(self, web3, empty_block):
        transaction_count = web3.vns.getBlockTransactionCount(empty_block['hash'])

        assert is_integer(transaction_count)
        assert transaction_count == 0

    def test_vns_getBlockTransactionCountByNumber_empty_block(self, web3, empty_block):
        transaction_count = web3.vns.getBlockTransactionCount(empty_block['number'])

        assert is_integer(transaction_count)
        assert transaction_count == 0

    def test_vns_getBlockTransactionCountByHash_block_with_txn(self, web3, block_with_txn):
        transaction_count = web3.vns.getBlockTransactionCount(block_with_txn['hash'])

        assert is_integer(transaction_count)
        assert transaction_count >= 1

    def test_vns_getBlockTransactionCountByNumber_block_with_txn(self, web3, block_with_txn):
        transaction_count = web3.vns.getBlockTransactionCount(block_with_txn['number'])

        assert is_integer(transaction_count)
        assert transaction_count >= 1

    def test_vns_getUncleCountByBlockHash(self, web3, empty_block):
        uncle_count = web3.vns.getUncleCount(empty_block['hash'])

        assert is_integer(uncle_count)
        assert uncle_count == 0

    def test_vns_getUncleCountByBlockNumber(self, web3, empty_block):
        uncle_count = web3.vns.getUncleCount(empty_block['number'])

        assert is_integer(uncle_count)
        assert uncle_count == 0

    def test_vns_getCode(self, web3, math_contract_address):
        code = web3.vns.getCode(math_contract_address)
        assert isinstance(code, HexBytes)
        assert len(code) > 0

    def test_vns_getCode_invalid_address(self, web3, math_contract):
        with pytest.raises(InvalidAddress):
            web3.vns.getCode(math_contract.address.lower())

    def test_vns_getCode_with_block_identifier(self, web3, emitter_contract):
        code = web3.vns.getCode(emitter_contract.address, block_identifier=web3.vns.blockNumber)
        assert isinstance(code, HexBytes)
        assert len(code) > 0

    def test_vns_sign(self, web3, unlocked_account_dual_type):
        signature = web3.vns.sign(
            unlocked_account_dual_type, text='Message tö sign. Longer than hash!'
        )
        assert is_bytes(signature)
        assert len(signature) == 32 + 32 + 1

        # test other formats
        hexsign = web3.vns.sign(
            unlocked_account_dual_type,
            hexstr='0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821'
        )
        assert hexsign == signature

        intsign = web3.vns.sign(
            unlocked_account_dual_type,
            0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821
        )
        assert intsign == signature

        bytessign = web3.vns.sign(
            unlocked_account_dual_type, b'Message t\xc3\xb6 sign. Longer than hash!'
        )
        assert bytessign == signature

        new_signature = web3.vns.sign(
            unlocked_account_dual_type, text='different message is different'
        )
        assert new_signature != signature

    def test_vns_signTransaction(self, web3, unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
            'nonce': 0,
        }
        result = web3.vns.signTransaction(txn_params)
        signatory_account = web3.vns.account.recoverTransaction(result['raw'])
        assert unlocked_account == signatory_account
        assert result['tx']['to'] == txn_params['to']
        assert result['tx']['value'] == txn_params['value']
        assert result['tx']['gas'] == txn_params['gas']
        assert result['tx']['gasPrice'] == txn_params['gasPrice']
        assert result['tx']['nonce'] == txn_params['nonce']

    def test_vns_sendTransaction_addr_checksum_required(self, web3, unlocked_account):
        non_checksum_addr = unlocked_account.lower()
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }

        with pytest.raises(InvalidAddress):
            invalid_params = dict(txn_params, **{'from': non_checksum_addr})
            web3.vns.sendTransaction(invalid_params)

        with pytest.raises(InvalidAddress):
            invalid_params = dict(txn_params, **{'to': non_checksum_addr})
            web3.vns.sendTransaction(invalid_params)

    def test_vns_sendTransaction(self, web3, unlocked_account_dual_type):
        txn_params = {
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)
        txn = web3.vns.getTransaction(txn_hash)

        assert is_same_address(txn['from'], txn_params['from'])
        assert is_same_address(txn['to'], txn_params['to'])
        assert txn['value'] == 1
        assert txn['gas'] == 21000
        assert txn['gasPrice'] == txn_params['gasPrice']

    def test_vns_sendTransaction_with_nonce(self, web3, unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            # Increased gas price to ensure transaction hash different from other tests
            'gasPrice': web3.vns.gasPrice * 2,
            'nonce': web3.vns.getTransactionCount(unlocked_account),
        }
        txn_hash = web3.vns.sendTransaction(txn_params)
        txn = web3.vns.getTransaction(txn_hash)

        assert is_same_address(txn['from'], txn_params['from'])
        assert is_same_address(txn['to'], txn_params['to'])
        assert txn['value'] == 1
        assert txn['gas'] == 21000
        assert txn['gasPrice'] == txn_params['gasPrice']
        assert txn['nonce'] == txn_params['nonce']

    def test_vns_replaceTransaction(self, web3, unlocked_account_dual_type):
        txn_params = {
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        txn_params['gasPrice'] = web3.vns.gasPrice * 2
        replace_txn_hash = web3.vns.replaceTransaction(txn_hash, txn_params)
        replace_txn = web3.vns.getTransaction(replace_txn_hash)

        assert is_same_address(replace_txn['from'], txn_params['from'])
        assert is_same_address(replace_txn['to'], txn_params['to'])
        assert replace_txn['value'] == 1
        assert replace_txn['gas'] == 21000
        assert replace_txn['gasPrice'] == txn_params['gasPrice']

    def test_vns_replaceTransaction_non_existing_transaction(
            self, web3, unlocked_account_dual_type):
        txn_params = {
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }
        with pytest.raises(TransactionNotFound):
            web3.vns.replaceTransaction(
                '0x98e8cc09b311583c5079fa600f6c2a3bea8611af168c52e4b60b5b243a441997',
                txn_params
            )

    # auto mine is enabled for this test
    def test_vns_replaceTransaction_already_mined(self, web3, unlocked_account_dual_type):
        txn_params = {
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        txn_params['gasPrice'] = web3.vns.gasPrice * 2
        with pytest.raises(ValueError):
            web3.vns.replaceTransaction(txn_hash, txn_params)

    def test_vns_replaceTransaction_incorrect_nonce(self, web3, unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)
        txn = web3.vns.getTransaction(txn_hash)

        txn_params['gasPrice'] = web3.vns.gasPrice * 2
        txn_params['nonce'] = txn['nonce'] + 1
        with pytest.raises(ValueError):
            web3.vns.replaceTransaction(txn_hash, txn_params)

    def test_vns_replaceTransaction_gas_price_too_low(self, web3, unlocked_account_dual_type):
        txn_params = {
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        txn_params['gasPrice'] = 9
        with pytest.raises(ValueError):
            web3.vns.replaceTransaction(txn_hash, txn_params)

    def test_vns_replaceTransaction_gas_price_defaulting_minimum(self, web3, unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        txn_params.pop('gasPrice')
        replace_txn_hash = web3.vns.replaceTransaction(txn_hash, txn_params)
        replace_txn = web3.vns.getTransaction(replace_txn_hash)

        assert replace_txn['gasPrice'] == 11  # minimum gas price

    def test_vns_replaceTransaction_gas_price_defaulting_strategy_higher(self,
                                                                         web3,
                                                                         unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        def higher_gas_price_strategy(web3, txn):
            return 20

        web3.vns.setGasPriceStrategy(higher_gas_price_strategy)

        txn_params.pop('gasPrice')
        replace_txn_hash = web3.vns.replaceTransaction(txn_hash, txn_params)
        replace_txn = web3.vns.getTransaction(replace_txn_hash)
        assert replace_txn['gasPrice'] == 20  # Strategy provides higher gas price

    def test_vns_replaceTransaction_gas_price_defaulting_strategy_lower(self,
                                                                        web3,
                                                                        unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': 10,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        def lower_gas_price_strategy(web3, txn):
            return 5

        web3.vns.setGasPriceStrategy(lower_gas_price_strategy)

        txn_params.pop('gasPrice')
        replace_txn_hash = web3.vns.replaceTransaction(txn_hash, txn_params)
        replace_txn = web3.vns.getTransaction(replace_txn_hash)
        # Strategy provices lower gas price - minimum preferred
        assert replace_txn['gasPrice'] == 11

    def test_vns_modifyTransaction(self, web3, unlocked_account):
        txn_params = {
            'from': unlocked_account,
            'to': unlocked_account,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        }
        txn_hash = web3.vns.sendTransaction(txn_params)

        modified_txn_hash = web3.vns.modifyTransaction(
            txn_hash, gasPrice=(txn_params['gasPrice'] * 2), value=2
        )
        modified_txn = web3.vns.getTransaction(modified_txn_hash)

        assert is_same_address(modified_txn['from'], txn_params['from'])
        assert is_same_address(modified_txn['to'], txn_params['to'])
        assert modified_txn['value'] == 2
        assert modified_txn['gas'] == 21000
        assert modified_txn['gasPrice'] == txn_params['gasPrice'] * 2

    @pytest.mark.parametrize(
        'raw_transaction, expected_hash',
        [
            (
                # address 0x39EEed73fb1D3855E90Cbd42f348b3D7b340aAA6
                '0xf8648085174876e8008252089439eeed73fb1d3855e90cbd42f348b3d7b340aaa601801ba0ec1295f00936acd0c2cb90ab2cdaacb8bf5e11b3d9957833595aca9ceedb7aada05dfc8937baec0e26029057abd3a1ef8c505dca2cdc07ffacb046d090d2bea06a',  # noqa: E501
                '0x1f80f8ab5f12a45be218f76404bda64d37270a6f4f86ededd0eb599f80548c13',
            ),
            (
                # private key 0x3c2ab4e8f17a7dea191b8c991522660126d681039509dc3bb31af7c9bdb63518
                # This is an unfunded account, but the transaction has a 0 gas price, so is valid.
                # It never needs to be mined, we just want the transaction hash back to confirm.
                HexBytes('0xf85f808082c35094d898d5e829717c72e7438bad593076686d7d164a80801ba005c2e99ecee98a12fbf28ab9577423f42e9e88f2291b3acc8228de743884c874a077d6bc77a47ad41ec85c96aac2ad27f05a039c4787fca8a1e5ee2d8c7ec1bb6a'),  # noqa: E501
                '0x98eeadb99454427f6aad7b558bac13e9d225512a6f5e5c11cf48e8d4067e51b5',
            ),
        ]
    )
    def test_vns_sendRawTransaction(self,
                                    web3,
                                    raw_transaction,
                                    funded_account_for_raw_txn,
                                    expected_hash):
        txn_hash = web3.vns.sendRawTransaction(raw_transaction)
        assert txn_hash == web3.toBytes(hexstr=expected_hash)

    def test_vns_call(self, web3, math_contract):
        coinbase = web3.vns.coinbase
        txn_params = math_contract._prepare_transaction(
            fn_name='add',
            fn_args=(7, 11),
            transaction={'from': coinbase, 'to': math_contract.address},
        )
        call_result = web3.vns.call(txn_params)
        assert is_string(call_result)
        result = decode_single('uint256', call_result)
        assert result == 18

    def test_vns_call_with_0_result(self, web3, math_contract):
        coinbase = web3.vns.coinbase
        txn_params = math_contract._prepare_transaction(
            fn_name='add',
            fn_args=(0, 0),
            transaction={'from': coinbase, 'to': math_contract.address},
        )
        call_result = web3.vns.call(txn_params)
        assert is_string(call_result)
        result = decode_single('uint256', call_result)
        assert result == 0

    def test_vns_estimateGas(self, web3, unlocked_account_dual_type):
        gas_estimate = web3.vns.estimateGas({
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
        })
        assert is_integer(gas_estimate)
        assert gas_estimate > 0

    def test_vns_estimateGas_with_block(self,
                                        web3,
                                        unlocked_account_dual_type):
        gas_estimate = web3.vns.estimateGas({
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
        }, 'latest')
        assert is_integer(gas_estimate)
        assert gas_estimate > 0

    def test_vns_getBlockByHash(self, web3, empty_block):
        block = web3.vns.getBlock(empty_block['hash'])
        assert block['hash'] == empty_block['hash']

    def test_vns_getBlockByHash_not_found(self, web3, empty_block):
        with pytest.raises(BlockNotFound):
            web3.vns.getBlock(UNKNOWN_HASH)

    def test_vns_getBlockByNumber_with_integer(self, web3, empty_block):
        block = web3.vns.getBlock(empty_block['number'])
        assert block['number'] == empty_block['number']

    def test_vns_getBlockByNumber_latest(self, web3, empty_block):
        current_block_number = web3.vns.blockNumber
        block = web3.vns.getBlock('latest')
        assert block['number'] == current_block_number

    def test_vns_getBlockByNumber_not_found(self, web3, empty_block):
        with pytest.raises(BlockNotFound):
            web3.vns.getBlock(12345)

    def test_vns_getBlockByNumber_pending(self, web3, empty_block):
        current_block_number = web3.vns.blockNumber
        block = web3.vns.getBlock('pending')
        assert block['number'] == current_block_number + 1

    def test_vns_getBlockByNumber_earliest(self, web3, empty_block):
        genesis_block = web3.vns.getBlock(0)
        block = web3.vns.getBlock('earliest')
        assert block['number'] == 0
        assert block['hash'] == genesis_block['hash']

    def test_vns_getBlockByNumber_full_transactions(self, web3, block_with_txn):
        block = web3.vns.getBlock(block_with_txn['number'], True)
        transaction = block['transactions'][0]
        assert transaction['hash'] == block_with_txn['transactions'][0]

    def test_vns_getTransactionByHash(self, web3, mined_txn_hash):
        transaction = web3.vns.getTransaction(mined_txn_hash)
        assert is_dict(transaction)
        assert transaction['hash'] == HexBytes(mined_txn_hash)

    def test_vns_getTransactionByHash_contract_creation(self,
                                                        web3,
                                                        math_contract_deploy_txn_hash):
        transaction = web3.vns.getTransaction(math_contract_deploy_txn_hash)
        assert is_dict(transaction)
        assert transaction['to'] is None, "to field is %r" % transaction['to']

    def test_vns_getTransactionByBlockHashAndIndex(self, web3, block_with_txn, mined_txn_hash):
        transaction = web3.vns.getTransactionByBlock(block_with_txn['hash'], 0)
        assert is_dict(transaction)
        assert transaction['hash'] == HexBytes(mined_txn_hash)

    def test_vns_getTransactionByBlockNumberAndIndex(self, web3, block_with_txn, mined_txn_hash):
        transaction = web3.vns.getTransactionByBlock(block_with_txn['number'], 0)
        assert is_dict(transaction)
        assert transaction['hash'] == HexBytes(mined_txn_hash)

    def test_vns_getTransactionReceipt_mined(self, web3, block_with_txn, mined_txn_hash):
        receipt = web3.vns.getTransactionReceipt(mined_txn_hash)
        assert is_dict(receipt)
        assert receipt['blockNumber'] == block_with_txn['number']
        assert receipt['blockHash'] == block_with_txn['hash']
        assert receipt['transactionIndex'] == 0
        assert receipt['transactionHash'] == HexBytes(mined_txn_hash)

    def test_vns_getTransactionReceipt_unmined(self, web3, unlocked_account_dual_type):
        txn_hash = web3.vns.sendTransaction({
            'from': unlocked_account_dual_type,
            'to': unlocked_account_dual_type,
            'value': 1,
            'gas': 21000,
            'gasPrice': web3.vns.gasPrice,
        })
        with pytest.raises(TransactionNotFound):
            web3.vns.getTransactionReceipt(txn_hash)

    def test_vns_getTransactionReceipt_with_log_entry(self,
                                                      web3,
                                                      block_with_txn_with_log,
                                                      emitter_contract,
                                                      txn_hash_with_log):
        receipt = web3.vns.getTransactionReceipt(txn_hash_with_log)
        assert is_dict(receipt)
        assert receipt['blockNumber'] == block_with_txn_with_log['number']
        assert receipt['blockHash'] == block_with_txn_with_log['hash']
        assert receipt['transactionIndex'] == 0
        assert receipt['transactionHash'] == HexBytes(txn_hash_with_log)

        assert len(receipt['logs']) == 1
        log_entry = receipt['logs'][0]

        assert log_entry['blockNumber'] == block_with_txn_with_log['number']
        assert log_entry['blockHash'] == block_with_txn_with_log['hash']
        assert log_entry['logIndex'] == 0
        assert is_same_address(log_entry['address'], emitter_contract.address)
        assert log_entry['transactionIndex'] == 0
        assert log_entry['transactionHash'] == HexBytes(txn_hash_with_log)

    def test_vns_getUncleByBlockHashAndIndex(self, web3):
        # TODO: how do we make uncles....
        pass

    def test_vns_getUncleByBlockNumberAndIndex(self, web3):
        # TODO: how do we make uncles....
        pass

    def test_vns_newFilter(self, web3):
        filter = web3.vns.filter({})

        changes = web3.vns.getFilterChanges(filter.filter_id)
        assert is_list_like(changes)
        assert not changes

        logs = web3.vns.getFilterLogs(filter.filter_id)
        assert is_list_like(logs)
        assert not logs

        result = web3.vns.uninstallFilter(filter.filter_id)
        assert result is True

    def test_vns_newBlockFilter(self, web3):
        filter = web3.vns.filter('latest')
        assert is_string(filter.filter_id)

        changes = web3.vns.getFilterChanges(filter.filter_id)
        assert is_list_like(changes)
        assert not changes

        # TODO: figure out why this fails in go-ethereum
        # logs = web3.vns.getFilterLogs(filter.filter_id)
        # assert is_list_like(logs)
        # assert not logs

        result = web3.vns.uninstallFilter(filter.filter_id)
        assert result is True

    def test_vns_newPendingTransactionFilter(self, web3):
        filter = web3.vns.filter('pending')
        assert is_string(filter.filter_id)

        changes = web3.vns.getFilterChanges(filter.filter_id)
        assert is_list_like(changes)
        assert not changes

        # TODO: figure out why this fails in go-ethereum
        # logs = web3.vns.getFilterLogs(filter.filter_id)
        # assert is_list_like(logs)
        # assert not logs

        result = web3.vns.uninstallFilter(filter.filter_id)
        assert result is True

    def test_vns_getLogs_without_logs(self, web3, block_with_txn_with_log):
        # Test with block range

        filter_params = {
            "fromBlock": 0,
            "toBlock": block_with_txn_with_log['number'] - 1,
        }
        result = web3.vns.getLogs(filter_params)
        assert len(result) == 0

        # the range is wrong
        filter_params = {
            "fromBlock": block_with_txn_with_log['number'],
            "toBlock": block_with_txn_with_log['number'] - 1,
        }
        result = web3.vns.getLogs(filter_params)
        assert len(result) == 0

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

    def test_vns_getLogs_with_logs(
            self,
            web3,
            block_with_txn_with_log,
            emitter_contract_address,
            txn_hash_with_log):

        def assert_contains_log(result):
            assert len(result) == 1
            log_entry = result[0]
            assert log_entry['blockNumber'] == block_with_txn_with_log['number']
            assert log_entry['blockHash'] == block_with_txn_with_log['hash']
            assert log_entry['logIndex'] == 0
            assert is_same_address(log_entry['address'], emitter_contract_address)
            assert log_entry['transactionIndex'] == 0
            assert log_entry['transactionHash'] == HexBytes(txn_hash_with_log)

        # Test with block range

        # the range includes the block where the log resides in
        filter_params = {
            "fromBlock": block_with_txn_with_log['number'],
            "toBlock": block_with_txn_with_log['number'],
        }
        result = web3.vns.getLogs(filter_params)
        assert_contains_log(result)

        # specify only `from_block`. by default `to_block` should be 'latest'
        filter_params = {
            "fromBlock": 0,
        }
        result = web3.vns.getLogs(filter_params)
        assert_contains_log(result)

        # Test with `address`

        # filter with emitter_contract.address
        filter_params = {
            "fromBlock": 0,
            "address": emitter_contract_address,
        }

    def test_vns_getLogs_with_logs_topic_args(
            self,
            web3,
            block_with_txn_with_log,
            emitter_contract_address,
            txn_hash_with_log):
        def assert_contains_log(result):
            assert len(result) == 1
            log_entry = result[0]
            assert log_entry['blockNumber'] == block_with_txn_with_log['number']
            assert log_entry['blockHash'] == block_with_txn_with_log['hash']
            assert log_entry['logIndex'] == 0
            assert is_same_address(log_entry['address'], emitter_contract_address)
            assert log_entry['transactionIndex'] == 0
            assert log_entry['transactionHash'] == HexBytes(txn_hash_with_log)

        # Test with None event sig

        filter_params = {
            "fromBlock": 0,
            "topics": [
                None,
                '0x000000000000000000000000000000000000000000000000000000000000d431'],
        }

        result = web3.vns.getLogs(filter_params)
        assert_contains_log(result)

        # Test with None indexed arg
        filter_params = {
            "fromBlock": 0,
            "topics": [
                '0x057bc32826fbe161da1c110afcdcae7c109a8b69149f727fc37a603c60ef94ca',
                None],
        }
        result = web3.vns.getLogs(filter_params)
        assert_contains_log(result)

    def test_vns_getLogs_with_logs_none_topic_args(
            self,
            web3):
        # Test with None overflowing
        filter_params = {
            "fromBlock": 0,
            "topics": [None, None, None],
        }

        result = web3.vns.getLogs(filter_params)
        assert len(result) == 0

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
        pending_call_result = math_contract.functions.counter().call(block_identifier='pending')

        assert block_hash_call_result == 0
        assert block_num_call_result == 0
        assert latest_call_result == 0
        assert default_call_result == 0

        if pending_call_result != 1:
            raise AssertionError("pending call result was %d instead of 1" % pending_call_result)

    def test_vns_uninstallFilter(self, web3):
        filter = web3.vns.filter({})
        assert is_string(filter.filter_id)

        success = web3.vns.uninstallFilter(filter.filter_id)
        assert success is True

        failure = web3.vns.uninstallFilter(filter.filter_id)
        assert failure is False

    def test_vns_getTransactionFromBlock_deprecation(self, web3, block_with_txn):
        with pytest.raises(DeprecationWarning):
            web3.vns.getTransactionFromBlock(block_with_txn['hash'], 0)

    def test_vns_getCompilers_deprecation(self, web3):
        with pytest.raises(DeprecationWarning):
            web3.vns.getCompilers()

    def test_vns_submitHashrate(self, web3):
        # node_id from EIP 1474: https://github.com/ethereum/EIPs/pull/1474/files
        node_id = '59daa26581d0acd1fce254fb7e85952f4c09d0915afd33d3886cd914bc7d283c'
        result = web3.vns.submitHashrate(5000, node_id)
        assert result is True

    def test_vns_submitWork(self, web3):
        nonce = 1
        pow_hash = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        mix_digest = '0xD1FE5700000000000000000000000000D1FE5700000000000000000000000000'
        result = web3.vns.submitWork(nonce, pow_hash, mix_digest)
        assert result is False
