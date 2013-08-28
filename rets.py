import requests

class Rets(object):

    def login(self, login_url, username, password):
        assert login_url, 'Login url cannot be empty'
        assert username,  'Username cannot be empty'
        assert password,  'Password cannot be empty'

        response = None
        try:
            response = requests.get(url=login_url, auth=(username, password)) 
        except Exception as e:
            print 'Error logging into RETS Server: {error}'.format(error=repr(e))

        return response
