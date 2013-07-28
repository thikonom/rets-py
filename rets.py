import requests

class Rets(object):

    def login(self, login_url, username, password):
        response = None
        try:
            assert login_url != '', 'Login url is empty'
            assert username  != '', 'Username is empty'
            assert password  != '', 'Password is empty'

            response = requests.get(url=login_url, auth=(username, password)) 
        except Exception as e:
            print 'Error logging into RETS Server: {error}'.format(error=repr(e))

        return response
