from time import time, sleep
import json
import logging 

from ....errors import  ExceptionWithKwargs
from ....calls import (
    common_get_request, common_post_request, files_post_request, get_uid, login,
    errmsg_to_string,
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
    g_result = common_post_request(
        url + '/txstatus',
        headers={'Authorization': 'Bearer ' + token},
        params={'data': json.dumps({'hashes': tx_hashes})}
    )
    results = {}
    for h in tx_hashes:
        result = g_result['results'][h]
        logger.debug("result: %s" % result)
        if 'errmsg' in result:
            logger.debug("    'errmsg' key is present")
            raise TxStatusHasErrmsgError(errmsg_to_string(result['errmsg']),
                        url=url, tx_hash=h, token=token,
                        verify_cert=verify_cert, result=result)

        if 'blockid' in result:
            logger.debug("    'blockid' key is present")
            if not result['blockid']:
                logger.debug("'blockid' is empty")
                raise TxStatusBlockIDIsEmptyError("blockid is EMPTY", url=url,
                        tx_hash=h, token=token, verify_cert=verify_cert,
                        result=result)
        else:
            logger.debug("    'blockid' key is absent")
            raise TxStatusNoBlockIDKeyError("'blockid key is absent", url=url,
                    tx_hash=h, token=token, verify_cert=verify_cert,
                    result=result)
        results[h] = result
    return results

def wait_tx_status(url, tx_hashes, token, timeout_secs=100, max_tries=100,
                   gap_secs=1, show_indicator=True, verify_cert=True):

    logger.debug("gap_secs: %d timeout_secs: %d max_tries: %d" %(gap_secs,
        timeout_secs, max_tries))
    end_time = time() + timeout_secs
    results = None
    cnt = 1
    while True:
        if show_indicator:
            print("Waiting (%d seconds) for the completion of the transaction (try %d/%max_tries) ..." % (timeout_secs, cnt, max_tries))
        logger.debug("try %d", cnt)
        no_block_id = False
        try:
            results = get_tx_status(url, tx_hashes, token,
                                    verify_cert=verify_cert)
            return results
        except TxStatusNoBlockIDKeyError as e: 
            no_block_id = True
        except TxStatusBlockIDIsEmptyError as e:
            no_block_id = True

        logger.debug("no_block_id: %s" % no_block_id)

        if time() > end_time:
            logger.debug("time exceeded")
            raise WaitTxStatusTimeoutError("time exceeded", url=url,
                    tx_hash=tx_hashes,
                    token=token,
                    verify_cert=verify_cert, result=results,
                    timeout_secs=timeout_secs, max_tries=max_tries,
                    gap_secs=gap_secs, tx_status_error=e)
        if cnt > max_tries:
            logger.debug("max tries exceeded")
            raise WaitTxStatusMaxTriesExceededError("max tries exceeded",
                    url=url,
                    tx_hash=tx_hashes,
                    token=token, verify_cert=verify_cert, result=results,
                    timeout_secs=timeout_secs, max_tries=max_tries,
                    gap_secs=gap_secs, tx_status_error=e)
        cnt += 1
        sleep(gap_secs)

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
