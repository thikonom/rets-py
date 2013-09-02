from StringIO import StringIO
from urllib import urlencode

from lxml import etree
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
        self.logged_in = False
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

        self.logged_in = True
        self.username = username
        self.password = password

        data = []
        #TODO add RetsException
        if response.text:
            tree = etree.parse(StringIO(response.text))
            #TODO parse response for rets_version 1.0
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

    def get_metadata(self, resource, klass):
        assert self.logged_in, 'You are not logged in'

        metadata_url = self.capability_urls.get('GETMETADATA') 
        assert metadata_url, 'No url for capability GetMetadata found'

        metadata_url += urlencode({'Type': 'METADATA-LOOKUP_TYPE',
                                   'ID': '',
                                   'Format': 'STANDARD-XML'})
        return self.get_metadata_table(resource, klass)

    #def get_metadata_table(self, resource, klass):

    #    assert resource, 'Resource parameter is required in get_metadata() request'
    #    assert klass, 'Class parameter is required in get_metadata() request'

    #    metadata_url = self.capability_urls['GETMETADATA']
    #    metadata_url += urlencode({'Type': 'METADATA-LOOKUP_TYPE',
    #                               'ID': '',
    #                               'Format': 'STANDARD-XML'})

    #    try:
    #        response = requests.get(url=metadata_url, auth=(self.username, self.password), header=self.headers)
    #    except Exception as e:
