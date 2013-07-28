from rets import *

import unittest

import httpretty

class RetsUnitTest(unittest.TestCase):

    def setUp(self):
        self.login_url = "http://www.rets.com/"
        self.username  = "admin"
        self.password  = "1234"

    def test_successful_login(self):
        httpretty.enable()
        mock_response = """<RETS ReplyCode=\"0\" ReplyText=\"Operation Successful\">\n<RETS-RESPONSE>\nBroker = FOO123\nMemberName = John Doe\nMetadataVersion = 5.00.000\nMinMetadataVersion = 5.00.000\nMetadataTimestamp = Wed, 1 June 2011 09:00:00 GMT\nMinMetadataTimestamp = Wed, 1 June 2011 09:00:00 GMT\nUser = BAR123\nLogin = http://foobar.com:1234/rets/login\nLogout = http://foobar.com:1234/rets/logout\nSearch = http://foobar.com:1234/rets/search\nGetMetadata = http://foobar.com:1234/rets/getmetadata\nGetObject = http://foobar.com:1234/rets/getobject\nTimeoutSeconds = 1800\n</RETS-RESPONSE>\n</RETS>"""

        httpretty.register_uri(httpretty.GET, self.login_url, body=mock_response)

        client = Rets()
        response = client.login(self.login_url, self.username, self.password)
        self.assertEqual(response.text, mock_response)
        httpretty.disable()

    def test_unable_to_login(self):
        mock_response = """<RETS ReplyCode=\"0\" ReplyText=\"Operation Successful\">\n<RETS-RESPONSE>\nBroker = FOO123\nMemberName = John Doe\nMetadataVersion = 5.00.000\nMinMetadataVersion = 5.00.000\nMetadataTimestamp = Wed, 1 June 2011 09:00:00 GMT\nMinMetadataTimestamp = Wed, 1 June 2011 09:00:00 GMT\nUser = BAR123\nLogin = http://foobar.com:1234/rets/login\nLogout = http://foobar.com:1234/rets/logout\nSearch = http://foobar.com:1234/rets/search\nGetMetadata = http://foobar.com:1234/rets/getmetadata\nGetObject = http://foobar.com:1234/rets/getobject\nTimeoutSeconds = 1800\n</RETS-RESPONSE>\n</RETS>"""
        httpretty.enable()
        httpretty.register_uri(httpretty.GET, self.login_url, body=mock_response)

        client = Rets()

        self.assertRaises(Exception, client.login("http://www.wrongurl.com", self.username, self.password))
        httpretty.disable()


if __name__ == '__main__':
    unittest.main()

