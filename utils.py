def assert_successful_response(response, url):
    response_code = response.status_code

    if response_code != 200:
        message = "Could not get URL [  {url} ] - HTTP response code: {code}".format(url, response_code)
        raise RetsHTTPException(response_code, message)
