import defi.contracts.bsc.apolloxV2.apolloxV2
import defi.contracts.bsc.apolloxV2.oracle
import defi.contracts.erc20
import defi.rpc.bsc
import defi.api.bsc.bsc_validator_set as bsc_validator_set
import defi.tokens
import pprint
from web3 import Web3
import time


class ApolloxV2:
    EXCHANGE_ID = 'apolloxv2'
    NETWORK_ID = 'bsc'

    def __init__(self, *args, **kwargs):
        self.w3 = None
        self.wallet_address = None
        self.private_key = None
        self.rpc_address = defi.rpc.bsc.rpc_endpoints[0]
        self.bnb_address = getattr(defi.tokens.bsc.WBNB, 'ADDRESS')  # wbnb reference is used for calculating bnb gas price in usd
        self.gas_buffer_factor = 1.0
        self.block_finality = None

        # set attributes directly from kwargs dynamically
        for key, value in kwargs.items():
            setattr(self, key, value)

        if not self.wallet_address or not self.private_key:
            raise ValueError('wallet address and key are required')

        # connect to available list of RPCs. Update block finality time after.
        self.auto_rpc_connect()

    # automatically connects to the immediately available RPC and updates the block finality time.
    def auto_rpc_connect(self):
        # check RPC connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_address))
        if not self._test_rpc_connection(self.rpc_address):
            for rpc in defi.rpc.bsc.rpc_endpoints:
                self.rpc_address = rpc
                self.w3 = Web3(Web3.HTTPProvider(self.rpc_address))
                if self._test_rpc_connection(self.rpc_address):
                    break
        # final check--
        if not self._test_rpc_connection(self.rpc_address):
            raise Exception('unable to connect to any rpc mainnet in registry!')
        # update block finality
        self._update_block_finality_time__()

    # tests the rpc node connection. it is recommended to call this before each operation.
    def _test_rpc_connection(self, rpc_url):
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        try:
            # Attempt to ping the node
            w3.manager.request_blocking("web3_clientVersion", [])
            return True
        except Exception as e:
            print(f"failed to connect to {rpc_url}: {e}")
            return False

    # fetches num active nodes, computes and updates block finality time
    def _update_block_finality_time__(self):
        params = {'rpc_address': self.rpc_address}
        # calculate block finality time
        validator_set = bsc_validator_set.BSCValidatorSet(**params)
        # bsc block finalization time == (2/3 * num_validator_nodes + 1)
        self.block_finality = 2/3 * validator_set.get_working_validator_count() + 1

    # checks the status of a broadcast txn
    def validate_transaction_status(self, txn_hash):
        self.auto_rpc_connect()
        transaction_receipt = self.w3.eth.get_transaction_receipt(txn_hash)
        if transaction_receipt is not None and transaction_receipt.get('status'):
            if transaction_receipt['status'] == 1:
                return True
            elif transaction_receipt['status'] == 0:
                return False
            else:
                return None

    # blocks execution until timeout or txn receipt is verified
    def await_transaction_receipt(self, txn_hash, timeout=120):
        """
        Check if the transaction has been mined into a block.

        :param txn_hash: Hash of the transaction to check.
        :return: True if the transaction has been mined, False otherwise.
        """

        # Using wait_for_transaction_receipt to wait until the transaction is mined
        return self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout)

    # blocks execution until block finality is reached for txn
    def await_finalization(self, txn_hash):
        txn_receipt = self.w3.eth.get_transaction_receipt(txn_hash)
        if txn_receipt is None:
            pass
            # raise InvalidTransaction('Transaction receipt not found.')
        initial_block = txn_receipt.blockNumber
        if not self.block_finality:
            raise ValueError('block finality must not be None and > 0')
        confirmation_block = initial_block + self.block_finality
        while self.w3.eth.block_number < confirmation_block:
            print(f"Current block is {self.w3.eth.block_number}, waiting for block {confirmation_block} for confirmation...")
            time.sleep(1)  # Wait for 15 seconds before checking again
        print(f"Transaction {txn_hash} has been finalized with at least {self.block_finality} confirmations.")

    # helper that returns gas amounts in ether units
    def get_txn_gas_fees(self, txn_hash):
        self.auto_rpc_connect()
        receipt = self.await_transaction_receipt(txn_hash)
        bnb_price = self.fetch_ticker(self.bnb_address)
        tokens_amount = receipt['gasUsed'] * receipt['effectiveGasPrice']
        return {
            'gas_price': receipt['effectiveGasPrice'],
            'gas_used': receipt['gasUsed'],
            'tokens_used': tokens_amount,
            'cost': (tokens_amount * bnb_price[0]) / (10 ** 26)
        }

    # returns the balance of a token in etherium units
    def balance_of(self, token_address):
        # contract info
        contract_address = token_address
        contract_abi = defi.contracts.erc20.abi
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=contract_abi)
        amount = contract.functions.balanceOf(Web3.to_checksum_address(self.wallet_address)).call()
        return amount

    # converts and returns a tokens balance to a human-readable format
    def convert_balance(self, token_address, amount):
        contract_address = token_address
        contract_abi = defi.contracts.erc20.abi
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=contract_abi)
        decimals = contract.functions.decimals().call()
        return amount / 10**decimals

    # returns the number of decimals for a token
    def decimals(self, token_address):
        # contract info
        contract_address = token_address
        contract_abi = defi.contracts.erc20.abi
        # serialize the contract into obj
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        decimals = contract.functions.decimals().call()
        return decimals

    # wrapper method for market data. only relevant for webservers with included CCXT implementation.
    def load_markets(self):
        return self.pairs_v3()

    # returns market data
    def pairs_v3(self):
        '''
            struct Pair {
            // BTC/USD
            string name;
            // BTC address
            address base;
            uint16 basePosition;
            IPairsManager.PairType pairType;
            IPairsManager.PairStatus status;

            uint16 slippageConfigIndex;
            uint16 slippagePosition;

            uint16 feeConfigIndex;
            uint16 feePosition;

            uint256 maxLongOiUsd;
            uint256 maxShortOiUsd;
            uint256 fundingFeePerBlockP;  // 1e18
            uint256 minFundingFeeR;       // 1e18
            uint256 maxFundingFeeR;       // 1e18
            // tier => LeverageMargin
            mapping(uint16 => LeverageMargin) leverageMargins;
            uint16 maxTier;

            uint40 longHoldingFeeRate;    // 1e12
        }
        :return:
        '''
        self.auto_rpc_connect()
        contract_address = defi.contracts.bsc.apolloxV2.apolloxV2.address
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        return contract.functions.pairsV3().call()

    # returns ticker for symbol and its decimals as a tuple
    def fetch_ticker(self, token_address):
        self.auto_rpc_connect()
        contract_address = Web3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        return contract.functions.getPriceFromChainlink(token_address).call()

    # returns all positions for a given market
    def get_positions(self, token_address):
        '''
            :param token_address: market where positions are deployed on
            :return:
                struct Position {
                bytes32 positionHash;
                // BTC/USD
                string pair;
                // pair.base
                address pairBase;
                address marginToken;
                bool isLong;
                uint96 margin;       // marginToken decimals
                uint80 qty;          // 1e10
                uint64 entryPrice;   // 1e8
                uint64 stopLoss;     // 1e8
                uint64 takeProfit;   // 1e8
                uint96 openFee;      // marginToken decimals
                uint96 executionFee; // marginToken decimals
                int256 fundingFee;   // marginToken decimals
                uint40 timestamp;
            }
        '''

        self.auto_rpc_connect()
        contract_address = self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        return contract.functions.getPositionsV2(self.w3.to_checksum_address(self.wallet_address), self.w3.to_checksum_address(token_address)).call()

    # fetches all open orders from exchange
    def get_limit_orders(self, token_address):
        self.auto_rpc_connect()
        contract_address = self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        return contract.functions.getLimitOrders(self.wallet_address, token_address).call()

    # cancel trade order
    def cancel_order(self, trade_hash):
        # verify the RPC connection and update block finality
        self.auto_rpc_connect()
        # contract info
        contract_address = self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        # serialize the contract into obj
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        trade_hash = bytes(trade_hash)
        txn = contract.functions.cancelLimitOrder(trade_hash)
        estimated_gas = txn.estimate_gas({'from': self.w3.to_checksum_address(self.wallet_address)})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = txn.build_transaction({
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'from': self.w3.to_checksum_address(self.wallet_address),
            'gas': buffered_gas,  # Set an appropriate gas limit
            'gasPrice': self.w3.eth.gas_price,
        })
        # Sign and send the transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # returns all order and trade history
    def get_order_and_trade_history(self, start=0, size=1):
        '''
        :param start: index position to begin search from
        :param size: number of results to return
        :return:
            struct OrderAndTradeHistory {
                bytes32 hash;
                uint40 timestamp;
                string pair;
                ActionType actionType;
                address tokenIn;
                bool isLong;
                uint96 amountIn;           // tokenIn decimals
                uint80 qty;                // 1e10
                uint64 entryPrice;         // 1e8

                uint96 margin;             // tokenIn decimals
                uint96 openFee;            // tokenIn decimals
                uint96 executionFee;       // tokenIn decimals

                uint64 closePrice;         // 1e8
                int96 fundingFee;          // tokenIn decimals
                uint96 closeFee;           // tokenIn decimals
                int96 pnl;                 // tokenIn decimals
                uint96 holdingFee;         // tokenIn decimals
                uint40 openTimestamp;
            }
        '''

        self.auto_rpc_connect()
        contract_address = self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        return contract.functions.getOrderAndTradeHistoryV2(self.wallet_address, start, size).call()

    # creates new market order
    def create_market_order(self, pair_base, is_long, token_in, amount_in, qty, price,
                                       take_profit=0, stop_loss=0, broker=0):
        """
        Open a new market order.

        :param pair_base: Address of the base pair (e.g., WETH address)
        :param is_long: Boolean indicating if it's a long position
        :param token_in: Address of the token being used as collateral (e.g., USDT)
        :param amount_in: Amount of collateral to use (in its native decimals)
        :param qty: Quantity of the order (1e10)
        :param price: Price of the limit order (1e8)
        :param stop_loss: Stop loss price (1e8), defaults to 0
        :param take_profit: Take profit price (1e8), defaults to 0
        :param broker: Broker fee (if any), defaults to 0
        """

        # verify the RPC connection and update block finality
        self.auto_rpc_connect()

        # check spending limits
        spending_limit = self.get_token_spending(defi.contracts.bsc.apolloxV2.apolloxV2.address, token_in)
        if amount_in > spending_limit:
            print(f'approving max spending limit for token {str(token_in)}')
            txn = self.set_token_spending(token_in)
            if not self.validate_transaction_status(txn):
                pass

        # Assuming the ABI is loaded into a variable called `contracts`
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address), abi=defi.contracts.bsc.apolloxV2.apolloxV2.abi)

        # Create the data input
        open_data_input = {
            'pairBase': Web3.to_checksum_address(pair_base),
            'isLong': is_long,
            'tokenIn': Web3.to_checksum_address(token_in),
            'amountIn': int(amount_in),
            'qty': int(qty),
            'price': int(price),
            'stopLoss': int(stop_loss),
            'takeProfit': int(take_profit),
            'broker': int(broker)
        }

        open_data_input = list(open_data_input.values())
        txn = contract.functions.openMarketTrade(open_data_input)

        estimated_gas = txn.estimate_gas({'from': self.wallet_address})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = txn.build_transaction({
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'from': self.w3.to_checksum_address(self.wallet_address),
            'gas': buffered_gas,  # Set an appropriate gas limit
            'gasPrice': self.w3.to_wei('3', 'gwei'),
            'chainId': 56,
        })
        # Sign and send the transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # creates new limit order
    def create_limit_order(self, pair_base, is_long, token_in, amount_in, qty, price,
                                      stop_loss=0, take_profit=0, broker=0):
        """
            Open a new limit order.

            :param pair_base: Address of the base pair (e.g., WETH address)
            :param is_long: Boolean indicating if it's a long position
            :param token_in: Address of the token being used as collateral (e.g., USDT)
            :param amount_in: Amount of collateral to use (in its native decimals)
            :param qty: Quantity of the order (1e10)
            :param price: Price of the limit order (1e8)
            :param stop_loss: Stop loss price (1e8), defaults to 0
            :param take_profit: Take profit price (1e8), defaults to 0
            :param broker: Broker fee (if any), defaults to 0
            """

        pair_base = self.w3.to_checksum_address(pair_base)
        token_in = self.w3.to_checksum_address(token_in)


        # verify the RPC connection and update block finality
        self.auto_rpc_connect()
        # check spending limits
        spending_limit = self.get_token_spending(defi.contracts.bsc.apolloxV2.apolloxV2.address, token_in)
        if amount_in > spending_limit:
            print(f'approving max spending limit for token {str(token_in)}')
            txn = self.set_token_spending(token_in)

        # Assuming the ABI is loaded into a variable called `contracts`
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address), abi=defi.contracts.bsc.apolloxV2.apolloxV2.abi)

        # Create the data input
        open_data_input = {
            'pairBase': pair_base,
            'isLong': is_long,
            'tokenIn': token_in,
            'amountIn': int(amount_in),
            'qty': int(qty),
            'price': int(price),
            'stopLoss': int(stop_loss),
            'takeProfit': int(take_profit),
            'broker': int(broker)
        }

        open_data_input = list(open_data_input.values())
        txn = contract.functions.openLimitOrder(open_data_input)

        estimated_gas = txn.estimate_gas({'from': self.wallet_address})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = txn.build_transaction({
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'from': self.wallet_address,
            'gas': buffered_gas,  # Set an appropriate gas limit
            'gasPrice': self.w3.eth.gas_price,
            'chainId': 56,
        })
        # Sign and send the transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # closes trade order
    def close_trade(self, trade_hash):
        """
        Open a new limit order.

        :param trade_hash: hash of the trade
        """
        self.auto_rpc_connect()
        contract_address = self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        contract_abi = defi.contracts.bsc.apolloxV2.apolloxV2.abi
        contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
        txn = contract.functions.closeTrade(trade_hash)
        estimated_gas = txn.estimate_gas({'from': self.wallet_address})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = txn.build_transaction({
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'from': self.w3.to_checksum_address(self.wallet_address),
            'gas': buffered_gas,  # Set an appropriate gas limit
            'gasPrice': self.w3.to_wei('3', 'gwei'),
            'chainId': 56,
        })
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # updates take profit order
    def update_trade_tp(self, order_hash, take_profit):
        """
            update an existing position tp/sl

            :param order_hash: hash of the position
            :param take_profit: new take profit, must be > 0
        """

        # verify the RPC connection and update block finality
        self.auto_rpc_connect()

        if not take_profit > 0:
            raise ValueError('take profit must be > 0')

        # Assuming the ABI is loaded into a variable called `contracts`
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address),
                                        abi=defi.contracts.bsc.apolloxV2.apolloxV2.abi)

        txn = contract.functions.updateTradeTp(order_hash, take_profit)

        estimated_gas = txn.estimate_gas({'from': self.wallet_address})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = txn.build_transaction({
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'from': self.w3.to_checksum_address(self.wallet_address),
            'gas': buffered_gas,  # Set an appropriate gas limit
            'gasPrice': self.w3.to_wei('3', 'gwei'),
            'chainId': 56,
        })
        # Sign and send the transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # updates stop loss order
    def update_trade_sl(self, order_hash, stop_loss):
        """
            update an existing position tp/sl

            :param order_hash: hash of the position
            :param stop_loss: new take profit, must be > 0
        """

        # verify the RPC connection and update block finality
        self.auto_rpc_connect()

        if not stop_loss >= 0:
            raise ValueError('stop loss must be >= 0')

        # Assuming the ABI is loaded into a variable called `contracts`
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address),
                                        abi=defi.contracts.bsc.apolloxV2.apolloxV2.abi)

        txn = contract.functions.updateTradeSl(order_hash, stop_loss)

        estimated_gas = txn.estimate_gas({'from': self.wallet_address})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = txn.build_transaction({
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'from': self.w3.to_checksum_address(self.wallet_address),
            'gas': buffered_gas,  # Set an appropriate gas limit
            'gasPrice': self.w3.to_wei('3', 'gwei'),
            'chainId': 56,
        })
        # Sign and send the transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # helper that updates both tp/sl at once
    def update_trade_tp_and_sl(self, order_hash, take_profit, stop_loss=None):

        # verify the RPC connection and update block finality
        self.auto_rpc_connect()

        tp_txn = self.update_trade_tp(order_hash, take_profit)

        sl_txn = None
        if stop_loss is not None:
            sl_txn = self.update_trade_sl(order_hash, stop_loss)

        return [tp_txn, sl_txn]

    # set how much positionRouter can spend. amount defaults to max if not specified.
    def set_token_spending(self, token_address, amount=2**256-1):
        self.auto_rpc_connect()
        token_address = self.w3.to_checksum_address(token_address)
        contract_abi = defi.contracts.erc20.abi
        contract = self.w3.eth.contract(address=token_address, abi=contract_abi)
        spender_address = self.w3.to_checksum_address(defi.contracts.bsc.apolloxV2.apolloxV2.address)
        txn = contract.functions.approve(spender_address, 2 ** 256 - 1)
        estimated_gas = txn.estimate_gas({'from': self.wallet_address})
        buffered_gas = int(estimated_gas * self.gas_buffer_factor)
        txn = {
            'to': token_address,
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'gas': buffered_gas,  # Temporary hardcoded gas limit
            'gasPrice': self.w3.eth.gas_price,
            'data': contract.encodeABI(fn_name='approve', args=[spender_address, 2 ** 256 - 1]),
            'chainId': 56
        }
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    # read how much positionRouter can spend
    def get_token_spending(self, spender_address, token_address):
        self.auto_rpc_connect()
        token_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(token_address), abi=defi.contracts.erc20.abi)
        allowance = token_contract.functions.allowance(self.w3.to_checksum_address(self.wallet_address), self.w3.to_checksum_address(spender_address)).call()
        return allowance

    # helper that returns the last placed position. useful for double verifying order placement by reading orders from the exchange.
    def sort_latest_position(self, positions, max_age_seconds=60):
        """
        Find the latest position within the last `max_age_seconds`.

        :param positions: List of position tuples.
        :param max_age_seconds: Maximum age of the position in seconds to be considered recent.
        :return: The latest position tuple or None if no recent position is found.
        """

        self.auto_rpc_connect()
        current_time = int(time.time())  # Current time in seconds
        recent_positions = []
        for position in positions:
            pos_timestamp = position[-2]
            time_delta = current_time - int(pos_timestamp)
            if time_delta <= max_age_seconds:
                recent_positions.append(position)
        if not recent_positions:
            return None
        # Assuming the last element of each position tuple is a timestamp in milliseconds
        latest_position = max(recent_positions, key=lambda pos: pos[-2])
        return latest_position


class_names = [name for name, obj in locals().items() if isinstance(obj, type)]
__all__ = class_names