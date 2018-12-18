import logging
import requests 
import urllib
import re
from requests.exceptions import RequestException

from .utils import dump_resp

logger = logging.getLogger(__name__)

def extract_param_by_name(string, name):
    pattern = "^" + name + "=(.*)$"
    l = list(filter(lambda x: x, (re.search(pattern, i).group(1) if re.search(pattern, i) else None for i in urllib.parse.unquote(string).split('&'))))
    if l:
        return l[0]

def errmsg_to_string(errmsg):
    msg = ""
    if 'type' in errmsg: 
        if msg:
            msg += " "
        msg += str(errmsg['type']).title()
    if 'error' in errmsg: 
        if msg:
            msg += ": "
        msg += str(errmsg['error'])
    return msg

class Error(Exception):
    pass

class NotResponseError(Error):
    pass

class ExtendedRequestException(RequestException):
    def __init__(self, *args, **kwargs):
        self.do_response_dump = kwargs.pop('do_response_dump', True) 
        super(ExtendedRequestException, self).__init__(*args, **kwargs)
        self.response_dump = None
        if self.do_response_dump:
            self.response_dump = dump_resp(self.response)

class ApiError(ExtendedRequestException):
    pass

class ApiError(RequestException):
    pass

class UnknownError(ApiError):
    brief = "Error hasn't been classified yet"

class NoErrorKeyError(ApiError):
    brief = "Error has no JSON body or has no 'error' key in it"

class ContractError(ApiError):
    brief = "Contract doesn't exist"

class DBNilError(ApiError):
    brief = "DB is invalid or doesn't exist"

class EcosystemError(ApiError):
    brief = "Ecosystem is invalid or doesn't exist"

class EmptyPublicKeyError(ApiError):
    brief = "Public key is undefined"
    def __init__(self, *args, **kwargs):
        super(EmptyPublicKeyError, self).__init__(*args, **kwargs)
        self.request_pubkey = None
        if hasattr(self, 'response') and self.response:
            self.request_pubkey = extract_param_by_name(self.response.request.body, 'pubkey')
        logger.debug("self.request_pubkey: %s" % self.request_pubkey)

class EmptySignatureError(ApiError):
    brief = "Signature is undefined"

class WrongHashError(ApiError):
    brief = "Hash is incorrect"

class HashNotFoundError(ApiError):
    brief = "Hash hasn't been found"

class AlreadInstalledError(ApiError):
    brief = "Platform is already installed"

class InvalidWalletError(ApiError):
    brief = "Wallet is invalid"

class ContentNotFoundError(ApiError):
    brief = "Content page or menu has not been found"

class NotInstalledError(ApiError):
    brief = "Platform is not installed. In this case, you need to run the install by the command"

class DBQueryError(ApiError):
    brief = "Incorrect DB Query"

class RecoveredError(ApiError):
    brief = "API recovered, panic error occured"

class RefreshTokenError(ApiError):
    brief = "Refresh token isn't valid"

class ServerError(ApiError):
    brief = "Server error. Returned in case of an error in the library functions golang. The msg field contains the error text,"

class SignatureError(ApiError):
    brief = "Signature is incorrect"

class LoginStateError(ApiError):
    brief = "Actor is not a membership of ecosystem"

class TableNotFoundError(ApiError):
    brief = "Table hasn't been found"

class TokenError(ApiError):
    brief = "Token is not valid"

class TokenExpiredError(ApiError):
    brief = "Token is expired"

class UnauthorizedError(ApiError):
    brief = "Unauthozied access"

class UndefinedValueError(ApiError):
    brief = "Valie is undefined"

class UnknownUIDError(ApiError):
    brief = "UID is unknown"

class VDEError(ApiError):
    brief = "VDE doesn't exist"

class VDECreatedError(ApiError):
    brief = "VDE already exists"


### Not mapped to E_<TYPE> @ backend errors ### begin ###

class BadSignatureError(ApiError):
    """ This error type has no appropriate E_<TYPE> @ backend now """
    def __init__(self, *args, **kwargs):
        super(BadSignatureError, self).__init__(*args, **kwargs)
        self.request_signature = None
        if hasattr(self, 'response') \
        and hasattr(self.response, 'request') \
        and hasattr(self.response.request, 'body'):
            self.request_signature = extract_param_by_name(self.response.request.body, 'signature')
        logger.debug("self.request_signature: %s" % self.request_signature)

class InvalidPublicKeyLenError(ApiError):
    """ This error type has no appropriate E_<TYPE> @ backend now """
    def __init__(self, *args, **kwargs):
        super(InvalidPublicKeyLenError, self).__init__(*args, **kwargs)
        self.request_signature = None
        if hasattr(self, 'response') \
        and hasattr(self.response, 'request') \
        and hasattr(self.response.request, 'body'):
            self.request_pubkey = extract_param_by_name(self.response.request.body, 'pubkey')
            self.request_pubkey_len = len(self.request_pubkey)
        logger.debug("self.request_pubkey %s; len: %d" % (self.request_pubkey, self.request_pubkey_len))

class ExceptionWithKwargs(Exception):
    def __init__(self, *args, **kwargs):
        super(ExceptionWithKwargs, self).__init__(*args)
        self.__dict__.update(kwargs)

class ExceptionWithKnownKwargs(ExceptionWithKwargs):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'param_names'):
            self.param_names = []
        msg_addon = ''
        for param in self.param_names:
            setattr(self, param, kwargs.get(param, None))
            #logger.debug("self.%s = %s" % (param, getattr(self, param)))
            if msg_addon:
                msg_addon += ' '
            msg_addon += "%s='%s'" % (param, getattr(self, param))

        if len(args) > 0:
            m = args[0] + ' ' + msg_addon
            args = (m,) + args[1:]
        super(ExceptionWithKnownKwargs, self).__init__(*args, **kwargs)

class TxStatusError(ExceptionWithKnownKwargs):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'param_names'):
            self.param_names = ['url', 'tx_hash', 'token', 'verify_cert',   
                                'result']
        super(TxStatusError, self).__init__(*args, **kwargs)

class TxStatusHasErrmsgError(TxStatusError):
    pass

class TxStatusNoBlockIDKeyError(TxStatusError):
    pass

class TxStatusBlockIDIsEmptyError(TxStatusError):
    pass

class WaitTxStatusError(TxStatusError):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'param_names'):
            self.param_names = ['url', 'tx_hash', 'token', 'verify_cert',
                                'result', 'timeout_secs', 'max_tries',
                                'gap_secs', 'tx_status_error']
        super(WaitTxStatusError, self).__init__(*args, **kwargs)

class WaitTxStatusTimeoutError(WaitTxStatusError):
    pass

class WaitTxStatusMaxTriesExceededError(WaitTxStatusError):
    pass

### Not mapped to E_<TYPE> @ backend errors #### end ####


class ErrorMutationError(Exception):
    pass

def get_error_by_id(error_id, msg=None):
    if not error_id:
        return NoErrorKeyError
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
        'E_SERVER': {
            'default':     ServerError,
            'msg_regex_map': {
                "encoding\/hex\: odd length hex string": BadSignatureError,
                "Incorrect sign": BadSignatureError,
                "invalid parameters len\(public\)": InvalidPublicKeyLenError,
            }
        },
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
    if error_id in errors_map:
        error = errors_map[error_id]
        error_mutated = False
        if type(error) == dict:
            if msg and 'msg_regex_map' in error:
                for pat, _error in error['msg_regex_map'].items():
                    if re.search(pat, msg, re.IGNORECASE):
                        error_mutated = True
                        error = _error
                        break
            if not error_mutated:
                if not 'default' in error:
                    raise ErrorMutationError("default class for the mutating error isn't set")
                error = error['default']
        error.error_mutated = error_mutated
        error.backend_error_id = error_id
        return error
    else:
        return UnknownError

