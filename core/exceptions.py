"""
Custom exception types.
Author: Jeff Mahler
"""
class RegistrationException(Exception):
    """ Failure in registration.
    """
    def __init__(self, *args, **kwargs):
         Exception.__init__(self, *args, **kwargs)
