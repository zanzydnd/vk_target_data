class Error(Exception):
    pass


class TooManyRequestsError(Error):
    """Is throwed when response code 601."""
    pass