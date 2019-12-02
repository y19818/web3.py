
def test_miner_setEtherbase(web3_empty):
    web3 = web3_empty
    assert web3.vns.coinbase == web3.vns.accounts[0]
    new_account = web3.personal.newAccount('this-is-a-password')
    web3.geth.miner.setEtherBase(new_account)
    assert web3.vns.coinbase == new_account
