from functools import (
    singledispatch,
)
import operator

from vns_account import (
    Account,
)
from vns_account.local import (
    LocalAccount,
)
from vns_keys.datatypes import (
    PrivateKey,
)
from vns_utils import (
    to_dict,
)

from web3._utils.formatters import (
    apply_formatter_if,
)
from web3._utils.rpc_abi import (
    TRANSACTION_PARAMS_ABIS,
    apply_abi_formatters_to_dict,
)
from web3._utils.toolz import (
    compose,
)
from web3._utils.transactions import (
    fill_nonce,
    fill_transaction_defaults,
)

from .abi import (
    STANDARD_NORMALIZERS,
)

to_hexstr_from_vns_key = operator.methodcaller('to_hex')


def is_vns_key(value):
    return isinstance(value, PrivateKey)


key_normalizer = compose(
    apply_formatter_if(is_vns_key, to_hexstr_from_vns_key),
)


@to_dict
def gen_normalized_accounts(val):
    if isinstance(val, (list, tuple, set,)):
        for i in val:
            account = to_account(i)
            yield account.address, account
    else:
        account = to_account(val)
        yield account.address, account
        return


@singledispatch
def to_account(val):
    raise TypeError(
        "key must be one of the types: "
        "vns_keys.datatype.PrivateKey, vns_account.local.LocalAccount, "
        "or raw private key as a hex string or byte string. "
        "Was of type {0}".format(type(val)))


@to_account.register(LocalAccount)
def _(val):
    return val


def private_key_to_account(val):
    normalized_key = key_normalizer(val)
    return Account.privateKeyToAccount(normalized_key)


to_account.register(PrivateKey, private_key_to_account)
to_account.register(str, private_key_to_account)
to_account.register(bytes, private_key_to_account)


def format_transaction(transaction):
    """Format transaction so that it can be used correctly in the signing middleware.

    Converts bytes to hex strings and other types that can be passed to the underlying layers.
    Also has the effect of normalizing 'from' for easier comparisons.
    """
    return apply_abi_formatters_to_dict(STANDARD_NORMALIZERS, TRANSACTION_PARAMS_ABIS, transaction)


def construct_sign_and_send_raw_middleware(private_key_or_account):
    """Capture transactions sign and send as raw transactions


    Keyword arguments:
    private_key_or_account -- A single private key or a tuple,
    list or set of private keys. Keys can be any of the following formats:
      - An vns_account.LocalAccount object
      - An vns_keys.PrivateKey object
      - A raw private key as a hex string or byte string
    """

    accounts = gen_normalized_accounts(private_key_or_account)

    def sign_and_send_raw_middleware(make_request, w3):

        format_and_fill_tx = compose(
            format_transaction,
            fill_transaction_defaults(w3),
            fill_nonce(w3))

        def middleware(method, params):
            if method != "vns_sendTransaction":
                return make_request(method, params)
            else:
                transaction = format_and_fill_tx(params[0])

            if 'from' not in transaction:
                return make_request(method, params)
            elif transaction.get('from') not in accounts:
                return make_request(method, params)

            account = accounts[transaction['from']]
            raw_tx = account.signTransaction(transaction).rawTransaction

            return make_request(
                "vns_sendRawTransaction",
                [raw_tx])

        return middleware

    return sign_and_send_raw_middleware
