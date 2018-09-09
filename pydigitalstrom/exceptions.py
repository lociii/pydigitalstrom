# -*- coding: UTF-8 -*-


class DSException(Exception):
    pass


class DSRequestException(DSException):
    pass


class DSUnsupportedException(DSException):
    pass


class DSCommandFailedException(DSException):
    pass


class DSParameterException(DSException):
    pass
