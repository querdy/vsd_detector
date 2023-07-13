from exceptions import DetectorBaseException


class VetisBaseException(DetectorBaseException):
    ...


class VetisRejectedError(VetisBaseException):
    ...


class VetisBadServerError(VetisBaseException):
    ...


class VetisNotResultError(VetisBaseException):
    ...
