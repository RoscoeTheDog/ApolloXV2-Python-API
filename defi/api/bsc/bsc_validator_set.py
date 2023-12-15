import defi.rpc.bsc
import defi.contracts.bsc.bsc_chain.bsc_validator_set as bsc_validator_set
import web3


class BSCValidatorSet:

    def __init__(self, *args, **kwargs):
        self.rpc_address = defi.rpc.bsc.rpc_endpoints[0]

        # set attributes directly from kwargs dynamically
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.auto_rpc_connect()

    def __test_rpc_connection(self, rpc_url):
        self.w3 = web3.Web3(web3.Web3.HTTPProvider(rpc_url))
        try:
            # Attempt to ping the node
            self.w3.manager.request_blocking("web3_clientVersion", [])
            return True
        except Exception as e:
            print(f"failed to connect to {rpc_url}: {e}")
            return False

    # automatically connects to the immediately available RPC and also updates the block finality time.
    def auto_rpc_connect(self):
        # check RPC connection
        self.w3 = web3.Web3(web3.Web3.HTTPProvider(self.rpc_address))
        if not self.__test_rpc_connection(self.rpc_address):
            for rpc in defi.rpc.bsc.rpc_endpoints:
                self.rpc_address = rpc
                self.w3 = web3.Web3(web3.Web3.HTTPProvider(self.rpc_address))
                if self.__test_rpc_connection(self.rpc_address):
                    break
        # final check--
        if not self.__test_rpc_connection(self.rpc_address):
            raise Exception('unable to connect to any rpc mainnet in registry!')

    def get_working_validator_count(self):
        address = bsc_validator_set.address
        abi = bsc_validator_set.abi

        contract = self.w3.eth.contract(address=web3.Web3.to_checksum_address(address), abi=abi)

        return contract.functions.getWorkingValidatorCount().call()

    def get_validators(self):
        address = bsc_validator_set.address
        abi = bsc_validator_set.abi

        contract = self.w3.eth.contract(address=web3.Web3.to_checksum_address(address), abi=abi)

        return contract.functions.getValidators().call()
