def rpc_gas_price_strategy(web3, transaction_params=None):
    """
    A simple gas price strategy deriving it's value from the vns_gasPrice JSON-RPC call.
    """
    return web3.manager.request_blocking("vns_gasPrice", [])
