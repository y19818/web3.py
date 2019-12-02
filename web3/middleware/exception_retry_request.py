from requests.exceptions import (
    ConnectionError,
    HTTPError,
    Timeout,
    TooManyRedirects,
)

whitelist = [
    'admin',
    'shh',
    'miner',
    'net',
    'txpool'
    'testing',
    'evm',
    'vns_protocolVersion',
    'vns_syncing',
    'vns_coinbase',
    'vns_mining',
    'vns_hashrate',
    'vns_gasPrice',
    'vns_accounts',
    'vns_blockNumber',
    'vns_getBalance',
    'vns_getStorageAt',
    'vns_getCode',
    'vns_getBlockByNumber',
    'vns_getBlockByHash',
    'vns_getBlockTransactionCountByNumber',
    'vns_getBlockTransactionCountByHash',
    'vns_getUncleCountByBlockNumber',
    'vns_getUncleCountByBlockHash',
    'vns_getTransactionByHash',
    'vns_getTransactionByBlockHashAndIndex',
    'vns_getTransactionByBlockNumberAndIndex',
    'vns_getTransactionReceipt',
    'vns_getTransactionCount',
    'vns_call',
    'vns_estimateGas',
    'vns_newBlockFilter',
    'vns_newPendingTransactionFilter',
    'vns_newFilter',
    'vns_getFilterChanges',
    'vns_getFilterLogs',
    'vns_getLogs',
    'vns_uninstallFilter',
    'vns_getCompilers',
    'vns_getWork',
    'vns_sign',
    'vns_sendRawTransaction',
    'personal_importRawKey',
    'personal_newAccount',
    'personal_listAccounts',
    'personal_lockAccount',
    'personal_unlockAccount',
    'personal_ecRecover',
    'personal_sign'
]


def check_if_retry_on_failure(method):
    root = method.split('_')[0]
    if root in whitelist:
        return True
    elif method in whitelist:
        return True
    else:
        return False


def exception_retry_middleware(make_request, web3, errors, retries=5):
    """
    Creates middleware that retries failed HTTP requests. Is a default
    middleware for HTTPProvider.
    """
    def middleware(method, params):
        if check_if_retry_on_failure(method):
            for i in range(retries):
                try:
                    return make_request(method, params)
                except errors:
                    if i < retries - 1:
                        continue
                    else:
                        raise
        else:
            return make_request(method, params)
    return middleware


def http_retry_request_middleware(make_request, web3):
    return exception_retry_middleware(
        make_request,
        web3,
        (ConnectionError, HTTPError, Timeout, TooManyRedirects)
    )
