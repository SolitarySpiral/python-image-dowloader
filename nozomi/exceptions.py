"""Nozomi exceptions."""

class NozomiException(Exception):
    """Base Nozomi package exception."""

class InvalidTagFormat(NozomiException):
    """The tag is not in valid format (i.e. empty string)."""

class InvalidUrlFormat(NozomiException):
    """The url is not in valid format."""
