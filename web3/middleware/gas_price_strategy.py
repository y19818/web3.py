from web3._utils.toolz import (
    assoc,
)


def gas_price_strategy_middleware(make_request, web3):
    """
    Includes a gas price using the gas price strategy
    """
    def middleware(method, params):
        if method == 'vns_sendTransaction':
            transaction = params[0]
            if 'gasPrice' not in transaction:
                generated_gas_price = web3.vns.generateGasPrice(transaction)
                if generated_gas_price is not None:
                    transaction = assoc(transaction, 'gasPrice', generated_gas_price)
                    return make_request(method, [transaction])
        return make_request(method, params)
    return middleware
