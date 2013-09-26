import rets

import unittest

import httpretty

class RetsUnitTest(unittest.TestCase):

    def setUp(self):
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
        httpretty.register_uri(httpretty.GET,'http://www.retserver.com/rets/login', body=mock_response)

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
        httpretty.register_uri(httpretty.GET, "http://www.wrongurl.com", status=401)

        client = rets.Rets()

        with self.assertRaises(AssertionError):
            client.login("http://www.wrongurl.com", self.username, self.password)
            self.assertEqual(client.capability_urls, {})
            self.assertEqual(client.server_info, {})

        httpretty.disable()


if __name__ == '__main__':
    unittest.main()
