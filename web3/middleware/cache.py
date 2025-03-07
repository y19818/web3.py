import functools
import threading
import time

import lru

from web3._utils.caching import (
    generate_cache_key,
)

SIMPLE_CACHE_RPC_WHITELIST = {
    'web3_clientVersion',
    'web3_sha3',
    'net_version',
    # 'net_peerCount',
    # 'net_listening',
    'vns_protocolVersion',
    # 'vns_syncing',
    # 'vns_coinbase',
    # 'vns_mining',
    # 'vns_hashrate',
    # 'vns_gasPrice',
    # 'vns_accounts',
    # 'vns_blockNumber',
    # 'vns_getBalance',
    # 'vns_getStorageAt',
    # 'vns_getTransactionCount',
    'vns_getBlockTransactionCountByHash',
    # 'vns_getBlockTransactionCountByNumber',
    'vns_getUncleCountByBlockHash',
    # 'vns_getUncleCountByBlockNumber',
    # 'vns_getCode',
    # 'vns_sign',
    # 'vns_sendTransaction',
    # 'vns_sendRawTransaction',
    # 'vns_call',
    # 'vns_estimateGas',
    'vns_getBlockByHash',
    # 'vns_getBlockByNumber',
    'vns_getTransactionByHash',
    'vns_getTransactionByBlockHashAndIndex',
    # 'vns_getTransactionByBlockNumberAndIndex',
    # 'vns_getTransactionReceipt',
    'vns_getUncleByBlockHashAndIndex',
    # 'vns_getUncleByBlockNumberAndIndex',
    # 'vns_getCompilers',
    # 'vns_compileLLL',
    # 'vns_compileSolidity',
    # 'vns_compileSerpent',
    # 'vns_newFilter',
    # 'vns_newBlockFilter',
    # 'vns_newPendingTransactionFilter',
    # 'vns_uninstallFilter',
    # 'vns_getFilterChanges',
    # 'vns_getFilterLogs',
    # 'vns_getLogs',
    # 'vns_getWork',
    # 'vns_submitWork',
    # 'vns_submitHashrate',
}


def _should_cache(method, params, response):
    if 'error' in response:
        return False
    elif 'result' not in response:
        return False

    if response['result'] is None:
        return False
    return True


def construct_simple_cache_middleware(
        cache_class,
        rpc_whitelist=SIMPLE_CACHE_RPC_WHITELIST,
        should_cache_fn=_should_cache):
    """
    Constructs a middleware which caches responses based on the request
    ``method`` and ``params``

    :param cache: Any dictionary-like object
    :param rpc_whitelist: A set of RPC methods which may have their responses cached.
    :param should_cache_fn: A callable which accepts ``method`` ``params`` and
        ``response`` and returns a boolean as to whether the response should be
        cached.
    """
    def simple_cache_middleware(make_request, web3):
        cache = cache_class()
        lock = threading.Lock()

        def middleware(method, params):
            lock_acquired = lock.acquire(blocking=False)

            try:
                if lock_acquired and method in rpc_whitelist:
                    cache_key = generate_cache_key((method, params))
                    if cache_key not in cache:
                        response = make_request(method, params)
                        if should_cache_fn(method, params, response):
                            cache[cache_key] = response
                        return response
                    return cache[cache_key]
                else:
                    return make_request(method, params)
            finally:
                if lock_acquired:
                    lock.release()
        return middleware
    return simple_cache_middleware


_simple_cache_middleware = construct_simple_cache_middleware(
    cache_class=functools.partial(lru.LRU, 256),
)


TIME_BASED_CACHE_RPC_WHITELIST = {
    # 'web3_clientVersion',
    # 'web3_sha3',
    # 'net_version',
    # 'net_peerCount',
    # 'net_listening',
    # 'vns_protocolVersion',
    # 'vns_syncing',
    'vns_coinbase',
    # 'vns_mining',
    # 'vns_hashrate',
    # 'vns_gasPrice',
    'vns_accounts',
    # 'vns_blockNumber',
    # 'vns_getBalance',
    # 'vns_getStorageAt',
    # 'vns_getTransactionCount',
    # 'vns_getBlockTransactionCountByHash',
    # 'vns_getBlockTransactionCountByNumber',
    # 'vns_getUncleCountByBlockHash',
    # 'vns_getUncleCountByBlockNumber',
    # 'vns_getCode',
    # 'vns_sign',
    # 'vns_sendTransaction',
    # 'vns_sendRawTransaction',
    # 'vns_call',
    # 'vns_estimateGas',
    # 'vns_getBlockByHash',
    # 'vns_getBlockByNumber',
    # 'vns_getTransactionByHash',
    # 'vns_getTransactionByBlockHashAndIndex',
    # 'vns_getTransactionByBlockNumberAndIndex',
    # 'vns_getTransactionReceipt',
    # 'vns_getUncleByBlockHashAndIndex',
    # 'vns_getUncleByBlockNumberAndIndex',
    # 'vns_getCompilers',
    # 'vns_compileLLL',
    # 'vns_compileSolidity',
    # 'vns_compileSerpent',
    # 'vns_newFilter',
    # 'vns_newBlockFilter',
    # 'vns_newPendingTransactionFilter',
    # 'vns_uninstallFilter',
    # 'vns_getFilterChanges',
    # 'vns_getFilterLogs',
    # 'vns_getLogs',
    # 'vns_getWork',
    # 'vns_submitWork',
    # 'vns_submitHashrate',
}


def construct_time_based_cache_middleware(
        cache_class,
        cache_expire_seconds=15,
        rpc_whitelist=TIME_BASED_CACHE_RPC_WHITELIST,
        should_cache_fn=_should_cache):
    """
    Constructs a middleware which caches responses based on the request
    ``method`` and ``params`` for a maximum amount of time as specified

    :param cache: Any dictionary-like object
    :param cache_expire_seconds: The number of seconds an item may be cached
        before it should expire.
    :param rpc_whitelist: A set of RPC methods which may have their responses cached.
    :param should_cache_fn: A callable which accepts ``method`` ``params`` and
        ``response`` and returns a boolean as to whether the response should be
        cached.
    """
    def time_based_cache_middleware(make_request, web3):
        cache = cache_class()
        lock = threading.Lock()

        def middleware(method, params):
            lock_acquired = lock.acquire(blocking=False)

            try:
                if lock_acquired and method in rpc_whitelist:
                    cache_key = generate_cache_key((method, params))
                    if cache_key in cache:
                        # check that the cached response is not expired.
                        cached_at, cached_response = cache[cache_key]
                        cached_for = time.time() - cached_at

                        if cached_for <= cache_expire_seconds:
                            return cached_response
                        else:
                            del cache[cache_key]

                    # cache either missed or expired so make the request.
                    response = make_request(method, params)

                    if should_cache_fn(method, params, response):
                        cache[cache_key] = (time.time(), response)

                    return response
                else:
                    return make_request(method, params)
            finally:
                if lock_acquired:
                    lock.release()
        return middleware
    return time_based_cache_middleware


_time_based_cache_middleware = construct_time_based_cache_middleware(
    cache_class=functools.partial(lru.LRU, 256),
)


BLOCK_NUMBER_RPC_WHITELIST = {
    # 'web3_clientVersion',
    # 'web3_sha3',
    # 'net_version',
    # 'net_peerCount',
    # 'net_listening',
    # 'vns_protocolVersion',
    # 'vns_syncing',
    # 'vns_coinbase',
    # 'vns_mining',
    # 'vns_hashrate',
    'vns_gasPrice',
    # 'vns_accounts',
    'vns_blockNumber',
    'vns_getBalance',
    'vns_getStorageAt',
    'vns_getTransactionCount',
    # 'vns_getBlockTransactionCountByHash',
    'vns_getBlockTransactionCountByNumber',
    # 'vns_getUncleCountByBlockHash',
    'vns_getUncleCountByBlockNumber',
    'vns_getCode',
    # 'vns_sign',
    # 'vns_sendTransaction',
    # 'vns_sendRawTransaction',
    'vns_call',
    'vns_estimateGas',
    # 'vns_getBlockByHash',
    'vns_getBlockByNumber',
    # 'vns_getTransactionByHash',
    # 'vns_getTransactionByBlockHashAndIndex',
    'vns_getTransactionByBlockNumberAndIndex',
    'vns_getTransactionReceipt',
    # 'vns_getUncleByBlockHashAndIndex',
    'vns_getUncleByBlockNumberAndIndex',
    # 'vns_getCompilers',
    # 'vns_compileLLL',
    # 'vns_compileSolidity',
    # 'vns_compileSerpent',
    # 'vns_newFilter',
    # 'vns_newBlockFilter',
    # 'vns_newPendingTransactionFilter',
    # 'vns_uninstallFilter',
    # 'vns_getFilterChanges',
    # 'vns_getFilterLogs',
    'vns_getLogs',
    # 'vns_getWork',
    # 'vns_submitWork',
    # 'vns_submitHashrate',
}


AVG_BLOCK_TIME_KEY = 'avg_block_time'
AVG_BLOCK_SAMPLE_SIZE_KEY = 'avg_block_sample_size'
AVG_BLOCK_TIME_UPDATED_AT_KEY = 'avg_block_time_updated_at'


def _is_latest_block_number_request(method, params):
    if method != 'vns_getBlockByNumber':
        return False
    elif params[:1] == ['latest']:
        return True
    return False


def construct_latest_block_based_cache_middleware(
        cache_class,
        rpc_whitelist=BLOCK_NUMBER_RPC_WHITELIST,
        average_block_time_sample_size=240,
        default_average_block_time=15,
        should_cache_fn=_should_cache):
    """
    Constructs a middleware which caches responses based on the request
    ``method``, ``params``, and the current latest block hash.

    :param cache: Any dictionary-like object
    :param cache_expire_seconds: The number of seconds an item may be cached
        before it should expire.
    :param rpc_whitelist: A set of RPC methods which may have their responses cached.
    :param should_cache_fn: A callable which accepts ``method`` ``params`` and
        ``response`` and returns a boolean as to whether the response should be
        cached.

    .. note::
        This middleware avoids re-fetching the current latest block for each
        request by tracking the current average block time and only requesting
        a new block when the last seen latest block is older than the average
        block time.
    """
    def latest_block_based_cache_middleware(make_request, web3):
        cache = cache_class()
        block_info = {}

        def _update_block_info_cache():
            avg_block_time = block_info.get(AVG_BLOCK_TIME_KEY, default_average_block_time)
            avg_block_sample_size = block_info.get(AVG_BLOCK_SAMPLE_SIZE_KEY, 0)
            avg_block_time_updated_at = block_info.get(AVG_BLOCK_TIME_UPDATED_AT_KEY, 0)

            # compute age as counted by number of blocks since the avg_block_time
            if avg_block_time == 0:
                avg_block_time_age_in_blocks = avg_block_sample_size
            else:
                avg_block_time_age_in_blocks = (
                    (time.time() - avg_block_time_updated_at) / avg_block_time
                )

            if avg_block_time_age_in_blocks >= avg_block_sample_size:
                # If the length of time since the average block time as
                # measured by blocks is greater than or equal to the number of
                # blocks sampled then we need to recompute the average block
                # time.
                latest_block = web3.vns.getBlock('latest')
                ancestor_block_number = max(
                    0,
                    latest_block['number'] - average_block_time_sample_size,
                )
                ancestor_block = web3.vns.getBlock(ancestor_block_number)
                sample_size = latest_block['number'] - ancestor_block_number

                block_info[AVG_BLOCK_SAMPLE_SIZE_KEY] = sample_size
                if sample_size != 0:
                    block_info[AVG_BLOCK_TIME_KEY] = (
                        (latest_block['timestamp'] - ancestor_block['timestamp']) / sample_size
                    )
                else:
                    block_info[AVG_BLOCK_TIME_KEY] = avg_block_time
                block_info[AVG_BLOCK_TIME_UPDATED_AT_KEY] = time.time()

            if 'latest_block' in block_info:
                latest_block = block_info['latest_block']
                time_since_latest_block = time.time() - latest_block['timestamp']

                # latest block is too old so update cache
                if time_since_latest_block > avg_block_time:
                    block_info['latest_block'] = web3.vns.getBlock('latest')
            else:
                # latest block has not been fetched so we fetch it.
                block_info['latest_block'] = web3.vns.getBlock('latest')

        lock = threading.Lock()

        def middleware(method, params):
            lock_acquired = lock.acquire(blocking=False)

            try:
                should_try_cache = (
                    lock_acquired and
                    method in rpc_whitelist and
                    not _is_latest_block_number_request(method, params)
                )
                if should_try_cache:
                    _update_block_info_cache()
                    latest_block_hash = block_info['latest_block']['hash']
                    cache_key = generate_cache_key((latest_block_hash, method, params))
                    if cache_key in cache:
                        return cache[cache_key]

                    response = make_request(method, params)
                    if should_cache_fn(method, params, response):
                        cache[cache_key] = response
                    return response
                else:
                    return make_request(method, params)
            finally:
                if lock_acquired:
                    lock.release()
        return middleware
    return latest_block_based_cache_middleware


_latest_block_based_cache_middleware = construct_latest_block_based_cache_middleware(
    cache_class=functools.partial(lru.LRU, 256),
    rpc_whitelist=BLOCK_NUMBER_RPC_WHITELIST,
)
