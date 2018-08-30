import logging
import requests

from requests.exceptions import RequestException
from nose import with_setup

from genesis_blockchain_api_client.errors import *
from genesis_blockchain_api_client.utils import dump_resp

logger = logging.getLogger(__name__)
api_root_url = 'http://127.0.0.1:17301/api/v2'

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_error_by_id():
    errors_map = {
        'E_CONTRACT':      ContractError,
        'E_DBNIL':         DBNilError,
        'E_ECOSYSTEM':     EcosystemError,
        'E_EMPTYPUBLIC':   EmptyPublicKeyError,
        'E_EMPTYSIGN':     EmptySignatureError,
        'E_HASHWRONG':     WrongHashError,
        'E_HASHNOTFOUND':  HashNotFoundError,
        'E_INSTALLED':     AlreadInstalledError,
        'E_INVALIDWALLET': InvalidWalletError,
        'E_NOTFOUND':      ContentNotFoundError,
        'E_NOTINSTALLED':  NotInstalledError,
        'E_QUERY':         DBQueryError, 
        'E_RECOVERED':     RecoveredError,
        'E_REFRESHTOKEN':  RefreshTokenError,
        'E_SERVER':        ServerError,
        'E_SIGNATURE':     SignatureError,
        'E_STATELOGIN':    LoginStateError,
        'E_TABLENOTFOUND': TableNotFoundError,
        'E_TOKEN':         TokenError,
        'E_TOKENEXPIRED':  TokenExpiredError,
        'E_UNAUTHORIZED':  UnauthorizedError,
        'E_UNDEFINEVAL':   UndefinedValueError,
        'E_UNKNOWNUID':    UnknownUIDError,
        'E_VDE':           VDEError,
        'E_VDECREATED':    VDECreatedError,
    }
    for error_id, error in errors_map.items():
        assert get_error_by_id(error_id) == error
    unknown_ids = ['E_SOMENEW', 'E_ANOTHERONE']
    for unknown_id in unknown_ids:
        assert get_error_by_id(unknown_id) == UnknownError

    mutating_errors = {
        'E_SERVER': {
            "encoding/hex: odd length hex string": BadSignatureError,
            "Incorrect sign": BadSignatureError,
            "invalid parameters len(public)": InvalidPublicKeyLenError,
        }
    }
    for error_id, msg_class_map in mutating_errors.items():
        for msg, exp_class in msg_class_map.items():
            assert get_error_by_id(error_id, msg=msg) == exp_class

#@with_setup(my_setup, my_teardown)
#def test_request_exception():
#    url = api_root_url + '/getuid'
#    resp = requests.get(url)
#    assert isinstance(resp, requests.Response)
#
#    try:
#        raise RequestException(response=resp)
#    except RequestException as e:
#        assert e.response == resp
#    resp_dump = dump_resp(resp)
#
#@with_setup(my_setup, my_teardown)
#def test_extended_request_exception():
#    url = api_root_url + '/getuid'
#    resp = requests.get(url)
#    assert isinstance(resp, requests.Response)
#
#    try:
#        raise ExtendedRequestException(response=resp)
#    except ExtendedRequestException as e:
#        assert e.response == resp
#        assert hasattr(e, 'response_dump')
#        assert hasattr(e, 'do_response_dump')
#        assert e.response_dump == None
#
#    try:
#        raise ExtendedRequestException(response=resp, do_response_dump=True)
#    except ExtendedRequestException as e:
#        assert e.response == resp
#        assert hasattr(e, 'response_dump')
#        assert hasattr(e, 'do_response_dump')
#        assert e.response_dump == dump_resp(resp)
#
#@with_setup(my_setup, my_teardown)
#def test_extended_request_exception():
#    pass
