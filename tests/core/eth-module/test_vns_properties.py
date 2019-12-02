def test_vns_protocolVersion(web3):
    assert web3.vns.protocolVersion == '63'


def test_vns_chainId(web3):
    assert web3.vns.chainId == '0x3d'
