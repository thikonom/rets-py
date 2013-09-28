from urlparse import urlparse
from urllib import urlencode
from StringIO import StringIO
import copy

from lxml import etree
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth

from .exceptions import RetsException
from .utils import assert_successful_response, login_required



UA_AUTH_TYPE = ['USER_AGENT_AUTH_RETS_1_7', # RETS 1.7 user agent authorization.
                'USER_AGENT_AUTH_INTEREALTY' # The Interealty variant of 1.7 user agent authorization.
               ]

class Rets(object):

    capabilities = {
        "ACTION": 1,
        "CHANGEPASSWORD": 1,
        "GETOBJECT": 1,
        "LOGIN": 1,
        "LOGINCOMPLETE": 1,
        "LOGOUT": 1,
        "SEARCH": 1,
        "GETMETADATA": 1,
        "SERVERINFORMATION": 1,
        "UPDATE": 1,
        "POSTOBJECT": 1,
        "GETPAYLOADLIST": 1
    }

    default_headers = {'RETS-Version': 'RETS/1.5',
                       'User-Agent':   'Rets-py/1.0'}

    use_basic_authentication = False
    ua_passwd = ""
    ua_auth_type = UA_AUTH_TYPE[0]

    def __init__(self, **kwargs):
        self.capability_urls = {}
        self.server_info = {}
        params = kwargs or {}
        headers = params.get('headers')
        self.headers = self.default_headers
        if headers:
            self.headers.update(headers)
        self.__logged_in = False
        self._session = None
        self._last_response_cache = {}
        
    def login(self, login_url, username, password, ua_passwd=''):
        self.__logged_in = False

        self._session = None

        self._last_response_cache.clear()

        assert login_url != '',  'Login url cannot be empty'
        assert username != '',   'Username cannot be empty'
        assert password != '',   'Password cannot be empty'

        uri_portions = urlparse(login_url)
        self.server_hostname = uri_portions.hostname
        self.server_port = uri_portions.port or 80
        self.server_protocol = uri_portions.scheme

        self.username = username
        self.password = password

        action = uri_portions.path
        
        base_req = requests.Request(method='GET', 
                                   headers=self.headers)
                             
        if self.use_basic_authentication:
            # try only basic authentication
            ba_req = copy.deepcopy(base_req)
            self.auth_methods = [ba_req]
        else:
            # try both basic and digest authentication
            ba_req = copy.deepcopy(base_req)
            ba_req.auth = HTTPBasicAuth(self.username, self.password)
            dg_req = copy.deepcopy(base_req)
            dg_req.auth = HTTPDigestAuth(self.username, self.password)
            self.auth_methods = [ba_req, dg_req]

        response = self.dorequest(action)

        if response.status_code == 401:
            response = self.dorequest(action)
            if response.status_code == 401:
                return False

        assert_successful_response(response, login_url)

        self._last_response_cache.update(response.headers)

        # update to last response header
        detected_rets_version = self._last_response_cache.get('rets-version')
        if detected_rets_version:
            self.headers['RETS-Version'] = detected_rets_version

        auth_support = self._last_response_cache.get('www-authenticate')
        if auth_support:
            if 'Basic' in auth_support: 
                self.auth_support_basic = True
            if 'Digest' in auth_support:
                self.auth_support_digest = True

        self._set_capability_urls(response)

        self.__logged_in = True

        return True

    def _set_capability_urls(self, response):
        tree = etree.parse(StringIO(response.text))
        root = tree.xpath('//RETS-RESPONSE')
        if not root:
            raise RetsException("Is not a RETS server.")

        for line in root[0].text.split('\n'):

            if not line.strip():
                continue
            try:
                key, value = line.split('=')
            except:
                raise RetsException('Invalid key value pair')

            key = key.strip().upper()
            value = value.strip()
            if key in self.capabilities or key.startswith('X-'):
                self.capability_urls[key] = value
            else:
                self.server_info[key] = value

    def dorequest(self, action, **kwargs):
        assert action != '', 'Action cannot be empty'

        # TODO set cookie if ua_passwd is not empty
        uri_portions = urlparse(action)
        if not uri_portions.netloc:
            # action is provided as a relative path
            request_url = self.server_protocol + '://' + self.server_hostname \
                          + ':' + str(self.server_port) + action
        else:
            # action is provided as an absolute path
            request_url = action

        request_args = ''
        if kwargs:
            request_args = urlencode(kwargs)
            request_url = "?".join([request_url, request_args])

        for req in self.auth_methods:
            req.url = request_url
            if self._last_response_cache.get('cookies'):
                req.cookies = self._last_response_cache['cookies']
            r = req.prepare()

            if self._session is None:
                # if there is no existing session
                self._session = requests.Session()
            response = self._session.send(r)

            if response.status_code == 200: 
                # save cookies for subsequent requests
                self._last_response_cache.setdefault('cookies', response.cookies)
                break

        return response

    @property
    def is_logged_in(self):
        return self.__logged_in

    @login_required
    def get_system_metadata(self):
        metadata_url = self.capability_urls.get('GETMETADATA')
        assert metadata_url != '', 'No url for capability GetMetadata found'

        req_params = {'Type': 'METADATA-SYSTEM',
                      'ID': '0',
                      'Format': 'STANDARD-XML'}

        response = self.dorequest(metadata_url, **req_params)

        system_metadata = {}
        tree = etree.parse(StringIO(response.text))
        root = tree.xpath('//System')
        if root:
            for element in root[0].iter('SystemID', 'SystemDescription', 'Comments', 'Version'):
                system_metadata[element.tag] = element.text or ''

        return system_metadata

    #def get_metadata(self, resource, klass):
    #    if not self.__logged_in:
    #        raise RetsException('You are not logged in')

    #    metadata_url = self.capability_urls.get('GETMETADATA')
    #    assert metadata_url, 'No url for capability GetMetadata found'

    #    metadata_url += urlencode({'Type': 'METADATA-LOOKUP_TYPE',
    #                               'ID': '',
    #                               'Format': 'STANDARD-XML'})
    #    return self.get_metadata_table(resource, klass)

    #def get_metadata_table(self, resource, klass):

    #    assert resource, 'Resource parameter is required in get_metadata() request'
    #    assert klass, 'Class parameter is required in get_metadata() request'

    #    metadata_url = self.capability_urls['GETMETADATA']
    #    metadata_url += urlencode({'Type': 'METADATA-LOOKUP_TYPE',
    #                               'ID': '',
    #                               'Format': 'STANDARD-XML'})
