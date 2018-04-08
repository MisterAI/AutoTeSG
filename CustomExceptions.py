#!/usr/bin/python


class TerminationException(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(TerminationException, self).__init__(message, errors)

class NoSolutionException(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(NoSolutionException, self).__init__(message, errors)