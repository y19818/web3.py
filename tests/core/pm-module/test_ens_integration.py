import pytest

from vns_utils import (
    to_bytes,
)
from ethpm import (
    ASSETS_DIR,
)

from ens import ENS
from web3.exceptions import (
    InvalidAddress,
)
from web3.pm import (
    VyperReferenceRegistry,
)


def bytes32(val):
    if isinstance(val, int):
        result = to_bytes(val)
    else:
        raise TypeError('val %r could not be converted to bytes')
    return result.rjust(32, b'\0')


@pytest.fixture
def ens_setup(deployer):
    # todo: move to module level once ethpm alpha stable
    ENS_MANIFEST = ASSETS_DIR / 'ens' / '1.0.1.json'
    ens_deployer = deployer(ENS_MANIFEST)
    w3 = ens_deployer.package.w3

    # ** Set up ENS contracts **

    # remove account that creates ENS, so test transactions don't have write access
    accounts = w3.vns.accounts
    ens_key = accounts.pop()

    # create ENS contract
    # values borrowed from:
    # https://github.com/ethereum/web3.py/blob/master/tests/ens/conftest.py#L109
    vns_labelhash = w3.keccak(text='vns')
   vns_namehash = bytes32(0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae)
    resolver_namehash = bytes32(0xfdd5d5de6dd63db72bbc2d487944ba13bf775b50a80805fe6fcaba9b0fba88f5)
    ens_package = ens_deployer.deploy("ENSRegistry", transaction={"from": ens_key})
    ens_contract = ens_package.deployments.get_instance("ENSRegistry")

    # create public resolver
    public_resolver_package = ens_deployer.deploy(
        "PublicResolver",
        ens_contract.address,
        transaction={"from": ens_key}
    )
    public_resolver = public_resolver_package.deployments.get_instance("PublicResolver")

    # set 'resolver.vns' to resolve to public resolver
    ens_contract.functions.setSubnodeOwner(
        b'\0' * 32,
        vns_labelhash,
        ens_key
    ).transact({'from': ens_key})

    ens_contract.functions.setSubnodeOwner(
        vns_namehash,
        w3.keccak(text='resolver'),
        ens_key
    ).transact({'from': ens_key})

    ens_contract.functions.setResolver(
        resolver_namehash,
        public_resolver.address
    ).transact({'from': ens_key})

    public_resolver.functions.setAddr(
        resolver_namehash,
        public_resolver.address
    ).transact({'from': ens_key})

    # create .vns auction registrar
    vns_registrar_package = ens_deployer.deploy(
        "FIFSRegistrar",
        ens_contract.address,
        vns_namehash,
        transaction={"from": ens_key}
    )
    vns_registrar = vns_registrar_package.deployments.get_instance("FIFSRegistrar")

    # set '.vns' to resolve to the registrar
    ens_contract.functions.setResolver(
        vns_namehash,
        public_resolver.address
    ).transact({'from': ens_key})

    public_resolver.functions.setAddr(
        vns_namehash,
        vns_registrar.address
    ).transact({'from': ens_key})

    # set owner of tester.vns to an account controlled by tests
    ens_contract.functions.setSubnodeOwner(
        vns_namehash,
        w3.keccak(text='tester'),
        w3.vns.accounts[2]  # note that this does not have to be the default, only in the list
    ).transact({'from': ens_key})

    # make the registrar the owner of the 'vns' name
    ens_contract.functions.setSubnodeOwner(
        b'\0' * 32,
        vns_labelhash,
        vns_registrar.address
    ).transact({'from': ens_key})
    return ENS.fromWeb3(w3, ens_contract.address)


@pytest.fixture
def ens(ens_setup, mocker):
    mocker.patch('web3.middleware.stalecheck._isfresh', return_value=True)
    ens_setup.web3.vns.defaultAccount = ens_setup.web3.vns.coinbase
    ens_setup.web3.enable_unstable_package_management_api()
    return ens_setup


def test_ens_must_be_set_before_ens_methods_can_be_used(ens):
    w3 = ens.web3
    with pytest.raises(InvalidAddress):
        w3.pm.set_registry("tester.vns")


def test_web3_ens(ens):
    w3 = ens.web3
    ns = ENS.fromWeb3(w3, ens.ens.address)
    w3.ens = ns
    registry = VyperReferenceRegistry.deploy_new_instance(w3)
    w3.ens.setup_address('tester.vns', registry.address)
    actual_addr = ens.address('tester.vns')
    w3.pm.set_registry('tester.vns')
    assert w3.pm.registry.address == actual_addr
    w3.pm.release_package('owned', '1.0.0', 'ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW')
    pkg_name, version, manifest_uri = w3.pm.get_release_data('owned', '1.0.0')
    assert pkg_name == 'owned'
    assert version == '1.0.0'
    assert manifest_uri == 'ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW'
