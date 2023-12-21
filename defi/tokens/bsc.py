import web3

# baseclass for bsc token types
class BaseBSCToken:
    NETWORK_ID = 'bsc'
    COLLATERAL_ID = None


class BTC(BaseBSCToken):
    COLLATERAL_ID = 'btc'
    ADDRESS = web3.Web3.to_checksum_address('0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c')


class ETH(BaseBSCToken):
    COLLATERAL_ID = 'eth'
    ADDRESS = web3.Web3.to_checksum_address('0x2170Ed0880ac9A755fd29B2688956BD959F933F8')


class BNB(BaseBSCToken):
    COLLATERAL_ID = 'bnb'
    ADDRESS = web3.Web3.to_checksum_address('0x095418A82BC2439703b69fbE1210824F2247D77c')


class WBNB(BaseBSCToken):
    COLLATERAL_ID = 'wbnb'
    ADDRESS = web3.Web3.to_checksum_address('0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')


class USDT(BaseBSCToken):
    COLLATERAL_ID = 'usdt'
    ADDRESS = web3.Web3.to_checksum_address('0x55d398326f99059ff775485246999027b3197955')


class USDC(BaseBSCToken):
    COLLATERAL_ID = 'usdc'
    ADDRESS = web3.Web3.to_checksum_address('0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d')


class CAKE(BaseBSCToken):
    COLLATERAL_ID = 'cake'
    ADDRESS = web3.Web3.to_checksum_address('0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82')


class FTM(BaseBSCToken):
    COLLATERAL_ID = 'ftm'
    ADDRESS = web3.Web3.to_checksum_address('0xAD29AbB318791D579433D831ed122aFeAf29dcfe')


class_names = [name for name, obj in locals().items() if isinstance(obj, type)]
__all__ = class_names