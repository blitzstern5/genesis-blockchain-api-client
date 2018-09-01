Genesis BlockChain API Client
=============================

# Installation

pip install git+http://github.com/blitzstern5/genesis-blockchain-api-client

# Usage

## Session Example 1

* Create a client session
* Generate private and public keys pair
* Login with your private key
* Call 'MainCondition' contract
* Wait for the transaction is completed. In this case 'Access denied' error will be raised

```
from genesis_blockchain_api_client.errors import TxStatusHasErrmsgError
from genesis_blockchain_api_client.session import Session

s = Session('http://localhost:17301/api/v2')
s.gen_keypair()
s.login()
s.prepare_tx(name='MainCondition')
s.call_contract()
try:
    sess.wait_tx_status()
except TxStatusHasErrmsgError as e:
    print(e)

```

## Session Example 2

* Create a client session
* Fetch block with ID 1 from the backend

```
from genesis_blockchain_api_client.session import Session

s = Session('http://localhost:17301/api/v2')
print(s.get_block(1))
try:
    sess.wait_tx_status()
except TxStatusHasErrmsgError as e:
    print(e)

```
