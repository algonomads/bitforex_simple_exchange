import requests
from pathlib import Path, os
import time
import hmac
import hashlib
import logging
from urllib.parse import urljoin, urlunsplit, urlsplit
from posixpath import normpath
from collections import OrderedDict
logging.basicConfig(level=logging.DEBUG)

class Exchange:
    _meta_name = 'bitforex'
    BASE_API_ENDPOINT = 'https://api.bitforex.com'
    API_SEGMENT = 'api'
    API_VERSION = 'v1'
    VALID_METHODS = ["GET", "POST", "DELETE", "PUT"]
    PATH_SEGMENTS = [API_SEGMENT, API_VERSION]
    DEFAULT_METHOD = "GET"
    
    ## Static methods (utils)
    @staticmethod
    def get_current_timestamp():
        return int(time.time()*1000.0)
    
    @staticmethod
    def encode_message(secret, message):
        return hmac.new(bytes(secret, 'latin-1'), 
                    msg=bytes(message, 'latin-1'), 
                    digestmod=hashlib.sha256).hexdigest()
    @staticmethod
    def keysort(params):
        return OrderedDict(sorted(params.items(), key=lambda t: t[0]))
    
    def __init__(self, log_level=logging.INFO):
        self.access_key = os.environ.get('BF_ACCESS_KEY')
        self.secret_key = os.environ.get('BF_SECRET_KEY')
        ## Utils
        self.logger = logging.getLogger(Exchange._meta_name)
        self.logger.setLevel(log_level)
        
        ## Request parameters
        self.api_base = Exchange.BASE_API_ENDPOINT
        self.path_segments = Exchange.PATH_SEGMENTS
        self.method_verb = Exchange.DEFAULT_METHOD
        self.params = {}
        
        self._build_url()
        
        ## URL Parse
        self.scheme, self.netloc, self.pathstr, self.querystr, self.fragment = urlsplit(self.api_base)
        
        ## Init class variables
        self.with_params()
        
    def with_keys(self, access_key=None, secret_key=None):
        self.access_key = access_key or self.access_key
        self.secret_key = secret_key or self.secret_key
        self._add_params({
            'accessKey': self.access_key,
        })
        return self
    
    def with_method(self, method_verb):
        if method_verb in Exchange.VALID_METHODS:
            self.method_verb = method_verb
        else:
            self.logger.error('"{}" not a valid method'.format(method_verb))
        return self
    
    def with_segment(self, segment):
        self.path_segments = Exchange.PATH_SEGMENTS + \
            [f for f in segment.split('/') if f != '']
        self._build_url()
        return self
        
    def with_params(self, **params):
        self.params = {
            'nonce': self.get_current_timestamp(),
            'accessKey': self.access_key,
            **params
        }
        self._build_url()
        return self
    
    def add_params(self, **params):
        self._add_params(params)
        self._build_url()
        return self
    
    def build_request(self, method_verb, segment=[], params={}):
        self.with_method(method_verb)
        self.with_segment(segment)
        self.with_params(**params)
        return self
    
    def _build_endpoint(self):
        segments = [''] + self.path_segments
        self.pathstr = normpath('/'.join(segments))
        self.api_endpoint = urljoin(self.api_base, self.pathstr)
    
    def _build_querystr(self):
        self.querystr = urlencode(self.keysort(self.params))
        
    def _add_params(self, params, add_nonce=True):
        self.params.update({
            **({'nonce': self.get_current_timestamp()} if add_nonce else {}),
            **params
        })
    
    def _build_url(self):
        self._build_endpoint()
        self._build_querystr()
        
    def _get_url(self):
        self._build_url()
        return urlunsplit((self.scheme, 
                    self.netloc, 
                    self.pathstr, 
                    self.querystr, ''))
    
    def _validate(self):
        assert self.access_key is not None, 'ACCESS_KEY not found, set BF_ACCESS_KEY in env'
        assert self.secret_key is not None, 'SECRET_KEY not found, set BF_SECRET_KEY in env'
        assert self.api_endpoint is not None, 'Corrupt built url'
        
    def _signData(self):
        _api_str = self._get_url().replace(self.api_base, '')
        self.logger.debug('API str {}'.format(_api_str))
        encoded_hash = self.encode_message(self.secret_key, _api_str)
        self._add_params({'signData': encoded_hash}, add_nonce=False)
    
    def _request(self):
        ## TODO: replace requests lib with std python urllib
        session = requests.session()
        return session.request(self.method_verb,
                               url=self.api_endpoint,
                               data=self.params)
    
    def test(self, skip_validation=False):
        self._build_url()
        self._signData()
        self.logger.debug('Endpoint {}'.format(self.api_endpoint))
        self.logger.debug('Path str {}'.format(self.pathstr))
        self.logger.debug('Query str {}'.format(self.querystr))
        self.logger.debug('FURL {}'.format(self._get_url()))
        
    def finalize(self, skip_validation=False):
        self._build_url()
        (not skip_validation) and self._validate()
        self._signData()
        self.logger.debug('Final URL {}'.format(self._get_url()))
        return self._request()
