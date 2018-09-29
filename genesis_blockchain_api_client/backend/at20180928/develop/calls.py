from time import time
import json
import logging 

from ....errors import  ExceptionWithKwargs
from ....calls import (
    common_get_request, common_post_request, files_post_request, get_uid, login,
    #TxStatusHasErrmsgError, TxStatusBlockIDIsEmptyError,
    #TxStatusNoBlockIDKeyError, WaitTxStatusTimeoutError,
    #WaitTxStatusMaxTriesExceededError,
)

logger = logging.getLogger(__name__)

class TxStatusError(ExceptionWithKwargs):
    def __init__(self, *args, **kwargs):
        super(TxStatusError, self).__init__(*args, **kwargs)
        params = ('url', 'tx_hashes', 'token', 'verify_cert', 'result')
        for param in params:
            setattr(self, param, kwargs.get(param, None))
            logger.debug("self.%s = %s" % (param, getattr(self, param)))

class TxStatusHasErrmsgError(TxStatusError):
    pass

class TxStatusNoBlockIDKeyError(TxStatusError):
    def __init__(self, *args, **kwargs):
        super(TxStatusNoBlockIDKeyError, self).__init__(*args, **kwargs)

class TxStatusBlockIDIsEmptyError(TxStatusError):
    def __init__(self, *args, **kwargs):
        super(TxStatusBlockIDIsEmptyError, self).__init__(*args, **kwargs)

class WaitTxStatusError(TxStatusError):
    def __init__(self, *args, **kwargs):
        super(WaitTxStatusError, self).__init__(*args, **kwargs)
        params = ('timeout_secs', 'max_tries', 'gap_secs',
                  'tx_status_error')
        for param in params:
            setattr(self, param, kwargs.get(param, None))
            logger.debug("self.%s = %s" % (param, getattr(self, param)))

class WaitTxStatusTimeoutError(WaitTxStatusError):
    pass

class WaitTxStatusMaxTriesExceededError(WaitTxStatusError):
    pass

def get_tx_status(url, tx_hashes, token, verify_cert=True):
    logger.debug("    requesting /txstatus/%s ..." % tx_hashes)
    result = common_post_request(
        url + '/txstatus',
        headers={'Authorization': 'Bearer ' + token},
        params={'data': json.dumps({'hashes': tx_hashes})}
    )
    return result

def get_contract_info(url, token, name='', data='', verify_cert=True,
                      send_pub_key=True):
    result = common_get_request(
        url + '/contract/' + name,
        headers={'Authorization': 'Bearer ' + token},
        verify_cert=verify_cert
    )
    return result

def send_tx(url, token, name='', data='', verify_cert=True, send_pub_key=True):
    result = files_post_request(
        url + '/sendTx/',
        headers={'Authorization': 'Bearer ' + token},
        data=data,
        verify_cert=verify_cert
    )
    return result
