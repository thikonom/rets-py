import urlparse
from urllib.parse import urlencode
from StringIO import StringIO

from lxml import etree
import requests

from exceptions import RetsException, RetsHTTPException
from utils import assert_successful_response


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

    DEFAULT_HEADERS = {'RETS-Version': 'RETS/1.5',
                       'User-Agent':   'Rets-py/1.0'}

    def __init__(self, **kwargs):
        self.capability_urls = {}
        self.server_info = {}
        params = kwargs or {}
        headers = params.get('headers')
        if headers:
            self.headers = self.DEFAULT_HEADERS.update(headers)
        self._logged_in = False

    def login(self, login_url, username, password):
        assert login_url != '', 'Login url cannot be empty'
        assert username !='',   'Username cannot be empty'
        assert password !='',   'Password cannot be empty'

        url_bits = urlparse.urlparse(login_url)
        self.server_hostname = url_bits.hostname
        self.server_port = url_bits.port or '80'
        self.server_protocol = url_bits.scheme

        self.capability_urls['Login'] = url_bits.path
        
        self.username = username
        self.password = password

        response = self.dorequest(self.capability_urls['Login'])

        if response.status_code == 401:
            response = dorequest()
            if response.status_code == 401:
                return false

        assert_successful_response(response, login_url)

        self._set_capability_urls(response)

        self.loggedin = True

        return True

    def _set_capability_urls(response):
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

    def dorequest(self, action, *args):
        assert action != '', 'Action cannot be empty'
       
        parse_result = urlparse.urlparse(action)  
        if not parse_result:
            # action has a relative path
            request_url = self.server_protocol + '://' + self.server_hostname + ':' + self.server_port + action
        else:
            request_url = action

        request_args = ''
        if params:
            request_args = urlencode(request_args)

        request_headers = ''
        for k,v in request_headers.iteritems():
            request_headers += "{key}:{value}\r\n".format(k,v) 

        response = requests.get(url=request_url, auth=(self.username, self.password), headers=request_headers)
