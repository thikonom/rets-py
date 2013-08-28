from rets import *

import unittest

import httpretty

class RetsUnitTest(unittest.TestCase):

    def setUp(self):
        self.login_url = "http://www.rets.com/"
        self.username  = "admin"
        self.password  = "1234"

    def test_successful_login(self):
        mock_response = """
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

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, self.login_url, body=mock_response)

        client = Rets()
        response = client.login(self.login_url, self.username, self.password)

        self.assertEqual(response.text, mock_response)
        httpretty.disable()

    def test_unable_to_login(self):
        mock_response = """
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

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, self.login_url, body=mock_response)

        client = Rets()

        self.assertRaises(Exception, client.login("http://www.wrongurl.com", self.username, self.password))
        httpretty.disable()


if __name__ == '__main__':
    unittest.main()
