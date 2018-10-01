# -*- coding: UTF-8 -*-


class DSException(Exception):
    pass


class DSRequestException(DSException):
    pass


class DSCommandFailedException(DSException):
    pass
