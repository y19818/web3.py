import math

from web3._utils.threads import (
    Timeout,
)
from web3._utils.toolz import (
    assoc,
    curry,
    merge,
)
from web3.exceptions import (
    TransactionNotFound,
)

VALID_TRANSACTION_PARAMS = [
    'from',
    'to',
    'gas',
    'gasPrice',
    'value',
    'data',
    'nonce',
    'chainId',
]

TRANSACTION_DEFAULTS = {
    'value': 0,
    'data': b'',
    'gas': lambda web3, tx: web3.vns.estimateGas(tx),
    'gasPrice': lambda web3, tx: web3.vns.generateGasPrice(tx) or web3.vns.gasPrice,
    'chainId': lambda web3, tx: int(web3.net.version),
}


@curry
def fill_nonce(web3, transaction):
    if 'from' in transaction and 'nonce' not in transaction:
        return assoc(
            transaction,
            'nonce',
            web3.vns.getTransactionCount(
                transaction['from'],
                block_identifier='pending'))
    else:
        return transaction


@curry
def fill_transaction_defaults(web3, transaction):
    """
    if web3 is None, fill as much as possible while offline
    """
    defaults = {}
    for key, default_getter in TRANSACTION_DEFAULTS.items():
        if key not in transaction:
            if callable(default_getter):
                if web3 is not None:
                    default_val = default_getter(web3, transaction)
                else:
                    raise ValueError("You must specify %s in the transaction" % key)
            else:
                default_val = default_getter
            defaults[key] = default_val
    return merge(defaults, transaction)


def wait_for_transaction_receipt(web3, txn_hash, timeout=120, poll_latency=0.1):
    with Timeout(timeout) as _timeout:
        while True:
            try:
                txn_receipt = web3.vns.getTransactionReceipt(txn_hash)
            except TransactionNotFound:
                txn_receipt = None
            # FIXME: The check for a null `blockHash` is due to parity's
            # non-standard implementation of the JSON-RPC API and should
            # be removed once the formal spec for the JSON-RPC endpoints
            # has been finalized.
            if txn_receipt is not None and txn_receipt['blockHash'] is not None:
                break
            _timeout.sleep(poll_latency)
    return txn_receipt


def get_block_gas_limit(web3, block_identifier=None):
    if block_identifier is None:
        block_identifier = web3.vns.blockNumber
    block = web3.vns.getBlock(block_identifier)
    return block['gasLimit']


def get_buffered_gas_estimate(web3, transaction, gas_buffer=100000):
    gas_estimate_transaction = dict(**transaction)

    gas_estimate = web3.vns.estimateGas(gas_estimate_transaction)

    gas_limit = get_block_gas_limit(web3)

    if gas_estimate > gas_limit:
        raise ValueError(
            "Contract does not appear to be deployable within the "
            "current network gas limits.  Estimated: {0}. Current gas "
            "limit: {1}".format(gas_estimate, gas_limit)
        )

    return min(gas_limit, gas_estimate + gas_buffer)


def get_required_transaction(web3, transaction_hash):
    current_transaction = web3.vns.getTransaction(transaction_hash)
    if not current_transaction:
        raise ValueError('Supplied transaction with hash {} does not exist'
                         .format(transaction_hash))
    return current_transaction


def extract_valid_transaction_params(transaction_params):
    extracted_params = {key: transaction_params[key]
                        for key in VALID_TRANSACTION_PARAMS if key in transaction_params}

    if extracted_params.get('data') is not None:
        if transaction_params.get('input') is not None:
            if extracted_params['data'] != transaction_params['input']:
                msg = 'failure to handle this transaction due to both "input: {}" and'
                msg += ' "data: {}" are populated. You need to resolve this conflict.'
                err_vals = (transaction_params['input'], extracted_params['data'])
                raise AttributeError(msg.format(*err_vals))
            else:
                return extracted_params
        else:
            return extracted_params
    elif extracted_params.get('data') is None:
        if transaction_params.get('input') is not None:
            return assoc(extracted_params, 'data', transaction_params['input'])
        else:
            return extracted_params
    else:
        raise Exception("Unreachable path: transaction's 'data' is either set or not set")


def assert_valid_transaction_params(transaction_params):
    for param in transaction_params:
        if param not in VALID_TRANSACTION_PARAMS:
            raise ValueError('{} is not a valid transaction parameter'.format(param))


def prepare_replacement_transaction(web3, current_transaction, new_transaction):
    if current_transaction['blockHash'] is not None:
        raise ValueError('Supplied transaction with hash {} has already been mined'
                         .format(current_transaction['hash']))
    if 'nonce' in new_transaction and new_transaction['nonce'] != current_transaction['nonce']:
        raise ValueError('Supplied nonce in new_transaction must match the pending transaction')

    if 'nonce' not in new_transaction:
        new_transaction = assoc(new_transaction, 'nonce', current_transaction['nonce'])

    if 'gasPrice' in new_transaction:
        if new_transaction['gasPrice'] <= current_transaction['gasPrice']:
            raise ValueError('Supplied gas price must exceed existing transaction gas price')
    else:
        generated_gas_price = web3.vns.generateGasPrice(new_transaction)
        minimum_gas_price = int(math.ceil(current_transaction['gasPrice'] * 1.1))
        if generated_gas_price and generated_gas_price > minimum_gas_price:
            new_transaction = assoc(new_transaction, 'gasPrice', generated_gas_price)
        else:
            new_transaction = assoc(new_transaction, 'gasPrice', minimum_gas_price)

    return new_transaction


def replace_transaction(web3, current_transaction, new_transaction):
    new_transaction = prepare_replacement_transaction(
        web3, current_transaction, new_transaction
    )
    return web3.vns.sendTransaction(new_transaction)
