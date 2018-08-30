Genesis BlockChain API CLient
=============================

# Installation

pip install git+http://github.com/blitzstern5/genesis-blockchain-api-client

# Usage

## Session Example 1

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
