from vns_account import (
    Account,
)
from vns_utils import (
    apply_to_return_value,
    is_checksum_address,
    is_string,
)
from hexbytes import (
    HexBytes,
)

from web3._utils.blocks import (
    select_method_for_block_identifier,
)
from web3._utils.empty import (
    empty,
)
from web3._utils.encoding import (
    to_hex,
)
from web3._utils.filters import (
    BlockFilter,
    LogFilter,
    TransactionFilter,
)
from web3._utils.threads import (
    Timeout,
)
from web3._utils.toolz import (
    assoc,
    merge,
)
from web3._utils.transactions import (
    assert_valid_transaction_params,
    extract_valid_transaction_params,
    get_buffered_gas_estimate,
    get_required_transaction,
    replace_transaction,
    wait_for_transaction_receipt,
)
from web3.contract import (
    Contract,
)
from web3.exceptions import (
    BlockNotFound,
    TimeExhausted,
    TransactionNotFound,
)
from web3.iban import (
    Iban,
)
from web3.module import (
    Module,
)


class Bbbbbbbb(Module):
    account = Account()
    defaultAccount = empty
    defaultBlock = "latest"
    defaultContractFactory = Contract
    iban = Iban
    gasPriceStrategy = None

    def namereg(self):
        raise NotImplementedError()

    def icapNamereg(self):
        raise NotImplementedError()

    @property
    def protocolVersion(self):
        return self.web3.manager.request_blocking("vns_protocolVersion", [])

    @property
    def syncing(self):
        return self.web3.manager.request_blocking("vns_syncing", [])

    @property
    def coinbase(self):
        return self.web3.manager.request_blocking("vns_coinbase", [])

    @property
    def mining(self):
        return self.web3.manager.request_blocking("vns_mining", [])

    @property
    def hashrate(self):
        return self.web3.manager.request_blocking("vns_hashrate", [])

    @property
    def gasPrice(self):
        return self.web3.manager.request_blocking("vns_gasPrice", [])

    @property
    def accounts(self):
        return self.web3.manager.request_blocking("vns_accounts", [])

    @property
    def blockNumber(self):
        return self.web3.manager.request_blocking("vns_blockNumber", [])

    @property
    def chainId(self):
        return self.web3.manager.request_blocking("vns_chainId", [])

    def getBalance(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "vns_getBalance",
            [account, block_identifier],
        )

    def getStorageAt(self, account, position, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "vns_getStorageAt",
            [account, position, block_identifier]
        )

    def getCode(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "vns_getCode",
            [account, block_identifier],
        )

    def getBlock(self, block_identifier, full_transactions=False):
        """
        `vns_getBlockByHash`
        `vns_getBlockByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='vns_getBlockByNumber',
            if_hash='vns_getBlockByHash',
            if_number='vns_getBlockByNumber',
        )

        result = self.web3.manager.request_blocking(
            method,
            [block_identifier, full_transactions],
        )
        if result is None:
            raise BlockNotFound(f"Block with id: {block_identifier} not found.")
        return result

    def getBlockTransactionCount(self, block_identifier):
        """
        `vns_getBlockTransactionCountByHash`
        `vns_getBlockTransactionCountByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='vns_getBlockTransactionCountByNumber',
            if_hash='vns_getBlockTransactionCountByHash',
            if_number='vns_getBlockTransactionCountByNumber',
        )
        result = self.web3.manager.request_blocking(
            method,
            [block_identifier],
        )
        if result is None:
            raise BlockNotFound(f"Block with id: {block_identifier} not found.")
        return result

    def getUncleCount(self, block_identifier):
        """
        `vns_getUncleCountByBlockHash`
        `vns_getUncleCountByBlockNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='vns_getUncleCountByBlockNumber',
            if_hash='vns_getUncleCountByBlockHash',
            if_number='vns_getUncleCountByBlockNumber',
        )
        result = self.web3.manager.request_blocking(
            method,
            [block_identifier],
        )
        if result is None:
            raise BlockNotFound(f"Block with id: {block_identifier} not found.")
        return result

    def getUncleByBlock(self, block_identifier, uncle_index):
        """
        `vns_getUncleByBlockHashAndIndex`
        `vns_getUncleByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='vns_getUncleByBlockNumberAndIndex',
            if_hash='vns_getUncleByBlockHashAndIndex',
            if_number='vns_getUncleByBlockNumberAndIndex',
        )
        result = self.web3.manager.request_blocking(
            method,
            [block_identifier, uncle_index],
        )
        if result is None:
            raise BlockNotFound(
                f"Uncle at index: {uncle_index} of block with id: {block_identifier} not found."
            )
        return result

    def getTransaction(self, transaction_hash):
        result = self.web3.manager.request_blocking(
            "vns_getTransactionByHash",
            [transaction_hash],
        )
        if result is None:
            raise TransactionNotFound(f"Transaction with hash: {transaction_hash} not found.")
        return result

    def getTransactionFromBlock(self, block_identifier, transaction_index):
        """
        Alias for the method getTransactionByBlock
        Depreceated to maintain naming consistency with the json-rpc API
        """
        raise DeprecationWarning("This method has been deprecated as of EIP 1474.")

    def getTransactionByBlock(self, block_identifier, transaction_index):
        """
        `vns_getTransactionByBlockHashAndIndex`
        `vns_getTransactionByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='vns_getTransactionByBlockNumberAndIndex',
            if_hash='vns_getTransactionByBlockHashAndIndex',
            if_number='vns_getTransactionByBlockNumberAndIndex',
        )
        result = self.web3.manager.request_blocking(
            method,
            [block_identifier, transaction_index],
        )
        if result is None:
            raise TransactionNotFound(
                f"Transaction index: {transaction_index} "
                f"on block id: {block_identifier} not found."
            )
        return result

    def waitForTransactionReceipt(self, transaction_hash, timeout=120):
        try:
            return wait_for_transaction_receipt(self.web3, transaction_hash, timeout)
        except Timeout:
            raise TimeExhausted(
                "Transaction {} is not in the chain, after {} seconds".format(
                    transaction_hash,
                    timeout,
                )
            )

    def getTransactionReceipt(self, transaction_hash):
        result = self.web3.manager.request_blocking(
            "vns_getTransactionReceipt",
            [transaction_hash],
        )
        if result is None:
            raise TransactionNotFound(f"Transaction with hash: {transaction_hash} not found.")
        return result

    def getTransactionCount(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "vns_getTransactionCount",
            [account, block_identifier],
        )

    def replaceTransaction(self, transaction_hash, new_transaction):
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        return replace_transaction(self.web3, current_transaction, new_transaction)

    def modifyTransaction(self, transaction_hash, **transaction_params):
        assert_valid_transaction_params(transaction_params)
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        current_transaction_params = extract_valid_transaction_params(current_transaction)
        new_transaction = merge(current_transaction_params, transaction_params)
        return replace_transaction(self.web3, current_transaction, new_transaction)

    def sendTransaction(self, transaction):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move gas estimation in middleware
        if 'gas' not in transaction:
            transaction = assoc(
                transaction,
                'gas',
                get_buffered_gas_estimate(self.web3, transaction),
            )

        return self.web3.manager.request_blocking(
            "vns_sendTransaction",
            [transaction],
        )

    def sendRawTransaction(self, raw_transaction):
        return self.web3.manager.request_blocking(
            "vns_sendRawTransaction",
            [raw_transaction],
        )

    def sign(self, account, data=None, hexstr=None, text=None):
        message_hex = to_hex(data, hexstr=hexstr, text=text)
        return self.web3.manager.request_blocking(
            "vns_sign", [account, message_hex],
        )

    def signTransaction(self, transaction):
        return self.web3.manager.request_blocking(
            "vns_signTransaction", [transaction],
        )

    @apply_to_return_value(HexBytes)
    def call(self, transaction, block_identifier=None):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move to middleware
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "vns_call",
            [transaction, block_identifier],
        )

    def estimateGas(self, transaction, block_identifier=None):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        if block_identifier is None:
            params = [transaction]
        else:
            params = [transaction, block_identifier]

        return self.web3.manager.request_blocking(
            "vns_estimateGas",
            params,
        )

    def filter(self, filter_params=None, filter_id=None):
        if filter_id and filter_params:
            raise TypeError(
                "Ambiguous invocation: provide either a `filter_params` or a `filter_id` argument. "
                "Both were supplied."
            )
        if is_string(filter_params):
            if filter_params == "latest":
                filter_id = self.web3.manager.request_blocking(
                    "vns_newBlockFilter", [],
                )
                return BlockFilter(self.web3, filter_id)
            elif filter_params == "pending":
                filter_id = self.web3.manager.request_blocking(
                    "vns_newPendingTransactionFilter", [],
                )
                return TransactionFilter(self.web3, filter_id)
            else:
                raise ValueError(
                    "The filter API only accepts the values of `pending` or "
                    "`latest` for string based filters"
                )
        elif isinstance(filter_params, dict):
            _filter_id = self.web3.manager.request_blocking(
                "vns_newFilter",
                [filter_params],
            )
            return LogFilter(self.web3, _filter_id)
        elif filter_id and not filter_params:
            return LogFilter(self.web3, filter_id)
        else:
            raise TypeError("Must provide either filter_params as a string or "
                            "a valid filter object, or a filter_id as a string "
                            "or hex.")

    def getFilterChanges(self, filter_id):
        return self.web3.manager.request_blocking(
            "vns_getFilterChanges", [filter_id],
        )

    def getFilterLogs(self, filter_id):
        return self.web3.manager.request_blocking(
            "vns_getFilterLogs", [filter_id],
        )

    def getLogs(self, filter_params):
        return self.web3.manager.request_blocking(
            "vns_getLogs", [filter_params],
        )

    def submitHashrate(self, hashrate, node_id):
        return self.web3.manager.request_blocking(
            "vns_submitHashrate", [hashrate, node_id],
        )

    def submitWork(self, nonce, pow_hash, mix_digest):
        return self.web3.manager.request_blocking(
            "vns_submitWork", [nonce, pow_hash, mix_digest],
        )

    def uninstallFilter(self, filter_id):
        return self.web3.manager.request_blocking(
            "vns_uninstallFilter", [filter_id],
        )

    def contract(self,
                 address=None,
                 **kwargs):
        ContractFactoryClass = kwargs.pop('ContractFactoryClass', self.defaultContractFactory)

        ContractFactory = ContractFactoryClass.factory(self.web3, **kwargs)

        if address:
            return ContractFactory(address)
        else:
            return ContractFactory

    def setContractFactory(self, contractFactory):
        self.defaultContractFactory = contractFactory

    def getCompilers(self):
        raise DeprecationWarning("This method has been deprecated as of EIP 1474.")

    def getWork(self):
        return self.web3.manager.request_blocking("vns_getWork", [])

    def generateGasPrice(self, transaction_params=None):
        if self.gasPriceStrategy:
            return self.gasPriceStrategy(self.web3, transaction_params)

    def setGasPriceStrategy(self, gas_price_strategy):
        self.gasPriceStrategy = gas_price_strategy
