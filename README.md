# ApolloXV2 Python API
 A python API wrapper for the ApolloXV2 defi derivatives exchange
 
Create an exchange instance and call wrapper methods. See `examples.py` for more details.
```python
from apolloxV2 import ApolloXV2
params = {
 'wallet_address': 'user_wallet_address',
 'private_key': 'user_private_key'
}
APX = ApolloXV2
print(APX.pairs_v3())
```
