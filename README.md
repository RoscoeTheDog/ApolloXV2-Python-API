# ApolloXV2 Python API
 A python API wrapper for the ApolloXV2 defi derivatives exchange

![image](https://github.com/RoscoeTheDog/ApolloXV2-Python-API/assets/54086262/d810942f-c0bb-4610-ac65-32727fd07a43)

ApolloXV2 is a great bsc on-chain solution for trading with features over V1 lets you manage risk better. Use 1-1001x leverage (depending on the market). Provide more than just stablecoins as collateral to trade with. Trades settle directly to your hotstorage wallet to reduce unncesssary exposure.

**Known-issues:**
+ Expression to calculate the order qty only works with USDT USDC stablecoins currently. I'm working on evaluating this out soon.
+ Not all tokens have been wrapped as a `BaseBSCToken` class in `defi/tokens/bsc.py`. it may need expanding on especially as more markets are released.

 
Example usage:
```python
from apolloxV2 import ApolloXV2
params = {
 'wallet_address': 'user_wallet_address',
 'private_key': 'user_private_key'
}
APX = ApolloXV2
print(APX.pairs_v3())

def create_market_order(wallet_address, private_key):
    params = {
        'wallet_address': wallet_address,
        'private_key': private_key,
        'gas_buffer_factor': 1.2
    }
    APX = apolloxV2.ApolloxV2(**params)

    print('beginning create market order!')
    print('fetching ticker BTC...')
    fetched = False
    btc_price = None
    btc_decimals = None
    while not fetched:
        try:
            btc_price, btc_decimals = APX.fetch_ticker(BTC.ADDRESS)
            fetched = True
        except Exception as e:
            pass

    # track the state of the positions before ordering
    positions_old = APX.get_positions(BTC.ADDRESS)

    '''
        UNIT CONVERSIONS.
        Use $30 USDT or more for testing,
        If leverage is too high you may experience more down draw before closing.
    '''
    # USDT has 18 decimals. You can use APX.decimals(token_address) to find this.
    amount_in = 15 * 10 ** 18
    # The minimum order requirement by the dex is 202 for now (post leverage)
    qty = int(202 * 10 ** 10 / (btc_price / 10 ** btc_decimals))
    # We'll use 1% slippage here, 0.1% is the minimum you can use or dex will throw error.
    target_price = int(btc_price * (1 + 0.01))
    is_long = True
    params = {
        'pair_base': BTC.ADDRESS,
        'is_long': is_long,
        'token_in': USDT.ADDRESS,
        'amount_in': amount_in,
        'qty': qty,
        'price': target_price,
        'take_profit': btc_price * (1 + 0.005), # take profit is required, sl is not.
    }

    print('creating market order...')
    pprint.pprint(params)
    txn_hash = None
    '''
        Warning: do not use while loops for orders.
        Verify the txn on chain and on-dex after submitting instead.
    '''
    try:
        txn_hash = APX.create_market_order(**params)
    except Exception as e:
        print(e)

    # verify txn status on-chain
    if txn_hash:
        receipt = APX.await_transaction_receipt(txn_hash)
        if APX.validate_transaction_status(txn_hash):
            print('txn pushed onchain successfully')

        print('gas cost summary:')
        pprint.pprint(APX.get_txn_gas_fees(txn_hash))

        # optional-- await block finality time before performing more actions.
        print('awaiting block finality time')
        APX.await_finalization(txn_hash)

        '''
            After txn verified on chain, check for the trade state on the dex.
            This is highly recommended; as a pending trade can still be cancelled and refunded by the dex.
        '''
        positions_new = APX.get_positions(BTC.ADDRESS)

        '''
            Because there is no way of checking pending pushed trades yet,
            developers will have to come up with a way of tracking the position state of the dex periodically.

            This way we have a reference point from before and after the order was pushed on chain,
            and we can filter through old positions list and new positions list 
            to determine if the opened trade is actually the one we just pushed.
        '''

        # filter through positions and match trade direction
        for pos_new in positions_new:
            if not pos_new[4] == is_long:
                continue
            for pos_old in positions_old:
                # skip if trade was already opened prior to order
                if pos_new[0] == pos_old[0]:
                    continue
                elif pos_new[4] == is_long:
                    print('found new trade on dex')


```
