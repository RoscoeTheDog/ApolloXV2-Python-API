# ApolloXV2 Python API
 A python API wrapper for the ApolloXV2 defi derivatives exchange

![image](https://github.com/RoscoeTheDog/ApolloXV2-Python-API/assets/54086262/d810942f-c0bb-4610-ac65-32727fd07a43)

ApolloXV2 is a great bsc on-chain solution for trading; with better features improving on its V1 predecesor which lets you manage risk better. Use 1-1001x leverage (depending on the market). Provide more than just stablecoins as collateral to trade with. Trades settle directly to your hotstorage wallet to reduce unncesssary exposure.

**Known-issues:**
+ Not all tokens have been wrapped as a `BaseBSCToken` class in the `defi/tokens/bsc.py` module. it may need expanding on especially as more markets are released.

This wrapper provides a python interface to ApolloxXV2 perp smart contracts [found here](https://github.com/apollox-finance/apollox-perp-contracts/tree/60638b7479362a1a1ac1bb3fead020c5082fe4cd/contracts). 
All essential methods to implement a strategy have been wrapped, while nonessentials have been ommited due to lack of a practical need.

You can read, create, limit, cancel, close, history, etc. The only thing not implemented currently is adding margin to existing trades (TBD).


Example usage.
```python
from apolloxV2 import ApolloXV2
from defi.tokens.bsc import *

# credentials are required for most operations. some few read commands exist
params = {
 'wallet_address': 'user_wallet_address',
 'private_key': 'user_private_key'
}

# to read markets from exchange
APX = ApolloXV2
print(APX.pairs_v3())

# token metadata contained in defi/tokns/bsc.py
print(BSC.ADDRESS)
print(USDT.ADDRESS)

# CREATE ORDERS V2
# set collateral and trading tokens
base_token = tokens.bsc.BTC
collateral_token = tokens.bsc.ETH
# specify order type
order_type = 'create_limit_order'

print('fetching base token ticker...')
fetched = False
base_price = None
base_decimals = None
while not fetched:
    try:
        base_price, base_decimals = APX.fetch_ticker(tokens.bsc.BTC)
        fetched = True
    except Exception as e:
        pass

print('fetching collateral token ticker...')
fetched = False
collateral_price = None
collateral_decimals = None
while not fetched:
    try:
        collateral_price, collateral_decimals = APX.fetch_ticker(collateral_token)
        fetched = True
    except Exception as e:
        pass

'''
   In this example we'll use about $13 of eth (0.055) as margin with 20x leverage to open a ~$200+ long position on BTC-USD.
'''
amount = 0.0055  # amount of collateral input currency
leverage = 20    
amount *= leverage
if order_type == 'create_market_order':
    amount_in = amount / leverage * 10**18    # this field type is always ^18 no matter the currency.
    token_swap_ratio = collateral_price / base_price
    amount_adjusted = amount_in * token_swap_ratio
    qty = (amount_adjusted/10**18) * 10**10 * leverage  # this is always ^10. undo other unit type conversions from prior.
    target_price = base_price * (1 + 0.001)
elif order_type == 'create_limit_order':
    amount_in = amount / leverage * 10**18    # this field type is always ^18 no matter the currency.
    target_price = base_price * (1 - 0.5)   #
    token_swap_ratio = collateral_price / target_price
    amount_adjusted = amount_in * token_swap_ratio
    qty = (amount_adjusted/10**18) * 10**10 * leverage  # this is always ^10. undo other unit type conversions from prior.

# test 10% take profit
take_profit = target_price + (1 + 0.1)

# build order params
params = {
    'pair_base': w3.to_checksum_address(base_token),
    'is_long': True,
    'token_in': w3.to_checksum_address(collateral_token),
    'amount_in': amount_in,
    'qty': qty,
    'price': target_price,
    'take_profit': take_profit,
}

txn_hash = None
if order_type == 'create_market_order':
    print('creating market order...')
    txn_hash = APX.create_market_order(**params)
elif order_type == 'create_limit_order':
    print('creating limit order...')
    txn_hash = APX.create_limit_order(**params)

if txn_hash:
    print('gas costs:')
    pprint.pprint(APX.get_txn_gas_fees(txn_hash))

    receipt = APX.await_transaction_receipt(txn_hash)
    if receipt:
        print('transaction verified')
        
    # block until state is immutable on-chain.
    APX.await_finalization(txn_hash)

```

Like my work? Buy me a drink! ☕🍺 <br>
[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=9TUKFAZRVLH4W)
