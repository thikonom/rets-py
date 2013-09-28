from functools import wraps

from .exceptions import RetsHTTPException

def login_required(fn):
    @wraps(fn)
    def _inner(*args, **kwargs):
        if args[0].is_logged_in:
            return fn(*args, **kwargs)
        raise RetsException('You are not logged in')
    return _inner

def assert_successful_response(response, url):
    response_code = response.status_code

    if response_code != 200:
        message = "Could not get URL [ {0} ] - HTTP response code: {1}".format(url, response_code)
        raise RetsHTTPException(response_code, message)
