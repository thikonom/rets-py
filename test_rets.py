import unittest

from mock import Mock, patch

import rets
from rets.exceptions import RetsHTTPException
from rets import Rets


class FakeResponse(object):
    """"FakeResponse class"""

class RetsUnitTest(unittest.TestCase):

    def setUp(self):
        self.username  = "admin"
        self.password  = "1234"

    def test_successful_login(self):
        fake_response_text = """
            <RETS ReplyCode="0" ReplyText="Operation Successful">
            <RETS-RESPONSE>
            MemberName=Retspy
            User=Retspy,0,Syndicator,Retspy
            Broker=NA
            MetadataVersion=1.00.00041
            MetadataTimestamp=2013-08-09T21:36:19
            MinMetadataTimestamp=2013-08-09T21:36:19
            TimeoutSeconds=1800000
            Action=/rets/action
            GetMetadata=/rets/getMetadata
            GetObject=/rets/getObject
            Login=/rets/login
            Logout=/rets/logout
            X-PostObject=/rets/postObject
            Search=/rets/search
            X-Selector=/rets/selector
            Update=/rets/update
            </RETS-RESPONSE>
            </RETS>
            """

            
        fakeobj = FakeResponse()
        fakeobj.__dict__ = {
                'text': fake_response_text,
                'status_code': 200,
                'headers': dict()
        }

        with patch.object(Rets, 'dorequest', return_value=fakeobj):
            client = rets.Rets()
            response = client.login('http://www.retserver.com/rets/login', self.username, self.password)

            self.assertEqual(response, True)
            self.assertEqual(client.server_info, {
                'BROKER': 'NA',
                'MEMBERNAME': 'Retspy',
                'METADATATIMESTAMP': '2013-08-09T21:36:19',
                'METADATAVERSION': '1.00.00041',
                'MINMETADATATIMESTAMP': '2013-08-09T21:36:19',
                'TIMEOUTSECONDS': '1800000',
                'USER': 'Retspy,0,Syndicator,Retspy'
            })
            self.assertEqual(client.capability_urls, {
               'ACTION': '/rets/action',
               'GETMETADATA': '/rets/getMetadata',
               'GETOBJECT': '/rets/getObject',
               'LOGIN': '/rets/login',
               'LOGOUT': '/rets/logout',
               'SEARCH': '/rets/search',
               'UPDATE': '/rets/update',
               'X-POSTOBJECT': '/rets/postObject',
               'X-SELECTOR': '/rets/selector'
            })  


    def test_unauthorized_login(self):
        fakeobj = FakeResponse()
        fakeobj.__dict__ = {
                'text': 'Unauthorized',
                'status_code': 401,
                'headers': dict()
        }

        with patch.object(Rets, 'dorequest', return_value=fakeobj):
            client = rets.Rets()
            response = client.login('http://www.retserver.com/rets/login', self.username, self.password)
            self.assertEqual(response, False)
            self.assertEqual(client.capability_urls, {})
            self.assertEqual(client.server_info, {})


    def test_unsuccessful_login(self):
        fakeobj = FakeResponse()
        fakeobj.__dict__ = {
                'text': '404: Not Found',
                'status_code': 404,
                'headers': dict()
        }

        with patch.object(Rets, 'dorequest', return_value=fakeobj), self.assertRaises(RetsHTTPException):
            client = rets.Rets()
            client.login("http://www.retserver.com/rets/login", self.username, self.password)
            self.assertEqual(client.capability_urls, {})
            self.assertEqual(client.server_info, {})


if __name__ == '__main__':
    unittest.main()
