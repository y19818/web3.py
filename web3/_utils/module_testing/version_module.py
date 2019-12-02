from vns_utils import (
    is_string,
)


class VersionModuleTest:
    def test_vns_protocolVersion(self, web3):
        protocol_version = web3.vns.protocolVersion

        assert is_string(protocol_version)
        assert protocol_version.isdigit()
