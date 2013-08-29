from lxml import etree
from StringIO import StringIO

import requests


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

    headers = {'RETS-Version': 'RETS/1.5',
               'User-Agent':   'Rets-py/1.0'}

    def __init__(self, **kwargs):
        self.capability_urls = {}
        self.server_info = {}
        params = kwargs or {}
        headers = params.get('headers')
        if headers:
            self.headers.update(headers)

    def connect(self, login_url, username, password):
        assert login_url, 'Login url cannot be empty'
        assert username,  'Username cannot be empty'
        assert password,  'Password cannot be empty'

        response = None
        try:
            response = requests.get(url=login_url, auth=(username, password), headers=self.headers) 
        except Exception as e:
            print 'Error logging into RETS Server: {error}'.format(error=repr(e))

        if response.status_code != 200:
            return False

        data = []
        #TODO add RetsException
        if response.text:
            tree = etree.parse(StringIO(response.text))
            root = tree.xpath('//RETS-RESPONSE')
            if not root:
                raise Exception("Is not a RETS server.")

            for line in root[0].text.split('\n'):

                if not line.strip():
                    continue
                try:
                    key, value = line.split('=')
                except:
                    raise Exception('Invalid key value pair')

                key = key.strip().upper()
                value = value.strip()
                if key in self.capabilities or key.startswith('X-'):
                    self.capability_urls[key] = value
                else:
                    self.server_info[key] = value

        return response.text
