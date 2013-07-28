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
        mock_response = """<RETS ReplyCode="0" ReplyText="V2.0.4 : Success">
                            MemberName=Elizabeth A Davis 
                            User=272, AGENT:BROKER OFFICE:OFFICE, 50, 272
                            Broker=MRIS,1
                            MetadataVersion=1.2.200
                            MinMetadataVersion=1.1.1
                            OfficeList=MRIS;1
                            TimeoutSeconds=1800
                            Search=http://cornerstone.mris.com:6103/platinum/search
                            GetObject=http://cornerstone.mris.com:6103/platinum/getobject
                            Login=http://cornerstone.mris.com:6103/platinum/login
                            GetMetadata=http://cornerstone.mris.com:6103/platinum/getmetadata
                            ChangePassword=http://cornerstone.mris.com:6103/platinum/changepassword
                            Logout=http://cornerstone.mris.com:6103/platinum/logout
                            </RETS>"""

        httpretty.register_uri(httpretty.GET, self.login_url, body=mock_response)

        client = Rets()
        response = client.login(self.login_url, self.username, self.password)

        self.assertEqual(response.text, mock_response)
        httpretty.disable()

    def test_unable_to_login(self):
        mock_response = """<RETS ReplyCode="0" ReplyText="V2.0.4 : Success">
                            MemberName=Elizabeth A Davis 
                            User=272, AGENT:BROKER OFFICE:OFFICE, 50, 272
                            Broker=MRIS,1
                            MetadataVersion=1.2.200
                            MinMetadataVersion=1.1.1
                            OfficeList=MRIS;1
                            TimeoutSeconds=1800
                            Search=http://cornerstone.mris.com:6103/platinum/search
                            GetObject=http://cornerstone.mris.com:6103/platinum/getobject
                            Login=http://cornerstone.mris.com:6103/platinum/login
                            GetMetadata=http://cornerstone.mris.com:6103/platinum/getmetadata
                            ChangePassword=http://cornerstone.mris.com:6103/platinum/changepassword
                            Logout=http://cornerstone.mris.com:6103/platinum/logout
                            </RETS>"""
        httpretty.enable()
        httpretty.register_uri(httpretty.GET, self.login_url, body=mock_response)

        client = Rets()

        self.assertRaises(Exception, client.login("http://www.wrongurl.com", self.username, self.password))
        httpretty.disable()


if __name__ == '__main__':
    unittest.main()

