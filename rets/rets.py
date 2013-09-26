from urlparse import urlparse
from urllib import urlencode
from StringIO import StringIO

from lxml import etree
import requests

from .exceptions import RetsException
from .utils import assert_successful_response


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

    def __init__(self, **kwargs):
        self.capability_urls = {}
        self.server_info = {}
        params = kwargs or {}
        headers = params.get('headers')
        self.headers = self.default_headers
        if headers:
            self.headers.update(headers)
        self.__logged_in = False

    def login(self, login_url, username, password):
        assert login_url != '', 'Login url cannot be empty'
        assert username != '',   'Username cannot be empty'
        assert password != '',   'Password cannot be empty'

        uri_portions = urlparse(login_url)
        self.server_hostname = uri_portions.hostname
        self.server_port = uri_portions.port or 80
        self.server_protocol = uri_portions.scheme

        self.username = username
        self.password = password

        action = uri_portions.path
        response = self.dorequest(action)

        if response.status_code == 401:
            response = self.dorequest(action)
            if response.status_code == 401:
                return False

        assert_successful_response(response, login_url)

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

    def dorequest(self, action, *args):
        assert action != '', 'Action cannot be empty'

        uri_portions = urlparse(action)
        if not uri_portions.netloc:
            # action is provided as a relative path
            request_url = self.server_protocol + '://' + self.server_hostname \
                          + ':' + str(self.server_port) + action
        else:
            # action is provided as an absolute path
            request_url = action

        request_args = ''
        if args:
            request_args = urlencode(args)

        response = requests.get(url=request_url,
                                auth=(self.username, self.password),
                                headers=self.headers)

        return response
