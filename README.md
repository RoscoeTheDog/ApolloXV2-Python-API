# ApolloXV2 Python API
 A python API wrapper for the ApolloXV2 defi derivatives exchange

![image](https://github.com/RoscoeTheDog/ApolloXV2-Python-API/assets/54086262/d810942f-c0bb-4610-ac65-32727fd07a43)

ApolloXV2 is a great bsc on-chain solution for trading with features over V1 lets you manage risk better. Use 1-1001x leverage (depending on the market). Provide more than just stablecoins as collateral to trade with. Trades settle directly to your hotstorage wallet to reduce unncesssary exposure.

**Known-issues:**
+ Expression to calculate the order qty only works with USDT USDC stablecoins currently. I'm working on evaluating this out soon.
+ Not all tokens have been wrapped as a `BaseBSCToken` class in `defi/tokens/bsc.py`. it may need expanding on especially as more markets are released.

 
Quickstart usage. See `examples.py` for a more in depth look at creating orders.
```python
from apolloxV2 import ApolloXV2
from defi.tokens.bsc import *

# credentials are required for most operations. some few read commands exist
params = {
 'wallet_address': 'user_wallet_address',
 'private_key': 'user_private_key'
}

APX = ApolloXV2
print(APX.pairs_v3())

# token metadata contained in defi/tokns/bsc.py
print(BSC.ADDRESS)
print(USDT.ADDRESS)
```

Like my work? Buy me a drink! ☕🍺 <br>
[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=9TUKFAZRVLH4W)
