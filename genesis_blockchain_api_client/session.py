import logging

from genesis_blockchain_tools import crypto

from .calls import (
    get_uid, sign_or_signtest, login, prepare_tx, call_contract,
    get_tx_status, wait_tx_status, get_max_block_id, get_blocks_data,
    get_block_data, get_version, get_block, get_blocks, get_block_metadata,
)

from .backend.versions import version_to_options, get_latest_version

logger = logging.getLogger(__name__)

class Session:
    def __init__(self, api_url, **kwargs):
        self.api_url = api_url
        self.backend_version = kwargs.get('backend_version',
                                          get_latest_version())
        if self.backend_version:
            self.set_backend_version(self.backend_version)
        self.verify_cert = kwargs.get('verify_cert', True)
        self.priv_key = kwargs.get('priv_key', None)
        self.pub_key = kwargs.get('pub_key', None)
        self.sign_fmt = kwargs.get('sign_fmt', 'DER')
        self.use_signtest = kwargs.get('use_signtest', False)
        self.crypto_backend = kwargs.get('crypto_backend', crypto)
        self.pub_key_fmt = kwargs.get('pub_key_fmt', 'RAW')
        self.send_pub_key = kwargs.get('send_pub_key', True)
        self.use_request_id = kwargs.get('use_request_id', True)
        self.b64decode_hashes = kwargs.get('b64decode_hashes', True)

        self.max_sign_tries = kwargs.get('max_sign_tries', 1)
        self.use_login_prefix = kwargs.get('use_login_prefix', True)

        #timeout_secs=10, max_tries=100, gap_secs=0.05
        self.wait_tx_timeout_secs = kwargs.get('wait_tx_timeout_secs', 10)
        self.wait_tx_max_tries = kwargs.get('wait_tx_max_tries', 20)
        self.wait_tx_gap_secs = kwargs.get('wait_tx_gap_secs', 0.5)

        self.uid = kwargs.get('uid', None)
        self.token = kwargs.get('token', None)
        self.l_result = None
        self.p_result = None
        self.c_result = None
        self.tx_status = None

    def set_backend_version(self, backend_version):
        if not backend_version:
            return
        self.backend_version = backend_version
        for name, value  in version_to_options(backend_version).items():
            setattr(self, name, value)

    def get_uid(self):
        self.uid, self.token = get_uid(self.api_url,
                                       verify_cert=self.verify_cert)

    def _sign_or_signtest(self, data):
        return sign_or_signtest(self.api_url, self.priv_key, data,
                                sign_fmt=self.sign_fmt,
                                use_signtest=self.use_signtest,
                                verify_cert=self.verify_cert,
                                crypto_backend=self.crypto_backend,
                                pub_key_fmt=self.pub_key_fmt)

    def login(self):
        if not self.uid:
            self.get_uid()
        self.l_result = login(self.api_url, self.priv_key, self.uid,
                                  self.token, sign_fmt=self.sign_fmt,
                                  use_signtest=self.use_signtest,
                                  verify_cert=self.verify_cert,
                                  crypto_backend=self.crypto_backend,
                                  sign_tries=self.max_sign_tries,
                                  use_login_prefix=self.use_login_prefix,
                                  pub_key_fmt=self.pub_key_fmt)

    def prepare_tx(self, name=None, data=None):
        self.contract_name = name
        self.contract_data = data
        self.p_result = prepare_tx(self.api_url, self.priv_key,
                                            self.contract_name,
                                            self.l_result['token'],
                                            self.contract_data,
                                            use_signtest=self.use_signtest,
                                            verify_cert=self.verify_cert,
                                            sign_fmt=self.sign_fmt,
                                            crypto_backend=self.crypto_backend,
                                            pub_key_fmt=self.pub_key_fmt)

    def gen_keypair(self):
        self.priv_key, self.pub_key = self.crypto_backend.gen_keypair(
                                                  pub_key_fmt=self.pub_key_fmt)

    def get_public_key(self):
        if not self.pub_key:
            self.pub_key = self.crypto_backend.get_public_key(self.priv_key,
                                                          fmt=self.pub_key_fmt)
        return self.pub_key

    def call_contract(self):
        if self.use_request_id:
            contract_name = self.p_result.get('request_id', None)
            contract_data = ''
        else:
            contract_name = self.contract_name
            contract_data = self.contract_data
        self.c_result = call_contract(self.api_url, self.get_public_key(),
                                      self.l_result['token'],
                                      self.p_result['time'],
                                      self.p_result['signature'], 
                                      name=contract_name,
                                      use_request_id=self.use_request_id,
                                      data=contract_data,
                                      verify_cert=self.verify_cert,
                                      send_pub_key=self.send_pub_key)

    def wait_tx_status(self):
        self.tx_status = wait_tx_status(self.api_url, self.c_result['hash'],
                                        self.l_result['token'],
                                        timeout_secs=self.wait_tx_timeout_secs,
                                        max_tries=self.wait_tx_max_tries,
                                        gap_secs=self.wait_tx_gap_secs,
                                        verify_cert=self.verify_cert)

    def get_version(self):
        return get_version(self.api_url, verify_cert=self.verify_cert)

    def get_max_block_id(self):
        return get_max_block_id(self.api_url, verify_cert=self.verify_cert)

    def get_block_metadata(self, block_id):
        return get_block_metadata(self.api_url, block_id,
                                  verify_cert=self.verify_cert)

    def get_blocks_data(self, block_id, count=None):
        return get_blocks_data(self.api_url, block_id, count=count, verify_cert=self.verify_cert)

    def get_block_data(self, block_id):
        return get_block_data(self.api_url, block_id, verify_cert=self.verify_cert)

    def get_blocks(self, block_id, count=None):
        return get_blocks(self.api_url, block_id, count=count, verify_cert=self.verify_cert, b64decode_hashes=self.b64decode_hashes)

    def get_block(self, block_id):
        return get_block(self.api_url, block_id, verify_cert=self.verify_cert,
                         b64decode_hashes=self.b64decode_hashes)

