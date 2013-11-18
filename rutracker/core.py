"""Core classes and functions."""

class Error(Exception):
    """The base class for all exception the module raises."""

    def __init__(self, *args, **kwargs):
        super(Error, self).__init__(args[0].format(*args[1:], **kwargs))
