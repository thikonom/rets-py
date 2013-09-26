def assert_successful_response(response, url):
    response_code = response.status_code

    if response_code != 200:
        message = "Could not get URL [ {0} ] - HTTP response code: {1}".format(url, response_code)
        raise RetsHTTPException(response_code, message)
