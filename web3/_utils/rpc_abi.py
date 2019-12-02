from vns_utils import (
    to_dict,
)

from web3._utils.abi import (
    map_abi_data,
)
from web3._utils.formatters import (
    apply_formatter_at_index,
)
from web3._utils.toolz import (
    curry,
)

TRANSACTION_PARAMS_ABIS = {
    'data': 'bytes',
    'from': 'address',
    'gas': 'uint',
    'gasPrice': 'uint',
    'nonce': 'uint',
    'to': 'address',
    'value': 'uint',
}

FILTER_PARAMS_ABIS = {
    'to': 'address',
    'address': 'address[]',
}

TRACE_PARAMS_ABIS = {
    'to': 'address',
    'from': 'address',
}

RPC_ABIS = {
    # vns     'vns_call': TRANSACTION_PARAMS_ABIS,
    'vns_estimateGas': TRANSACTION_PARAMS_ABIS,
    'vns_getBalance': ['address', None],
    'vns_getBlockByHash': ['bytes32', 'bool'],
    'vns_getBlockTransactionCountByHash': ['bytes32'],
    'vns_getCode': ['address', None],
    'vns_getLogs': FILTER_PARAMS_ABIS,
    'vns_getStorageAt': ['address', 'uint', None],
    'vns_getTransactionByBlockHashAndIndex': ['bytes32', 'uint'],
    'vns_getTransactionByHash': ['bytes32'],
    'vns_getTransactionCount': ['address', None],
    'vns_getTransactionReceipt': ['bytes32'],
    'vns_getUncleCountByBlockHash': ['bytes32'],
    'vns_newFilter': FILTER_PARAMS_ABIS,
    'vns_sendRawTransaction': ['bytes'],
    'vns_sendTransaction': TRANSACTION_PARAMS_ABIS,
    'vns_signTransaction': TRANSACTION_PARAMS_ABIS,
    'vns_sign': ['address', 'bytes'],
    'vns_submitHashrate': ['uint', 'bytes32'],
    'vns_submitWork': ['bytes8', 'bytes32', 'bytes32'],
    # personal
    'personal_sendTransaction': TRANSACTION_PARAMS_ABIS,
    'personal_lockAccount': ['address'],
    'personal_unlockAccount': ['address', None, None],
    'personal_sign': [None, 'address', None],
    'trace_call': TRACE_PARAMS_ABIS,
    # parity
    'parity_listStorageKeys': ['address', None, None, None],
}


@curry
def apply_abi_formatters_to_dict(normalizers, abi_dict, data):
    fields = list(set(abi_dict.keys()) & set(data.keys()))
    formatted_values = map_abi_data(
        normalizers,
        [abi_dict[field] for field in fields],
        [data[field] for field in fields],
    )
    formatted_dict = dict(zip(fields, formatted_values))
    return dict(data, **formatted_dict)


@to_dict
def abi_request_formatters(normalizers, abis):
    for method, abi_types in abis.items():
        if isinstance(abi_types, list):
            yield method, map_abi_data(normalizers, abi_types)
        elif isinstance(abi_types, dict):
            single_dict_formatter = apply_abi_formatters_to_dict(normalizers, abi_types)
            yield method, apply_formatter_at_index(single_dict_formatter, 0)
        else:
            raise TypeError("ABI definitions must be a list or dictionary, got %r" % abi_types)
