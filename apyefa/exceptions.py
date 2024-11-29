class EfaConnectionError(IOError):
    pass


class EfaParameterError(ValueError):
    pass


class EfaParseError(AttributeError):
    pass


class EfaResponseInvalid(ValueError):
    pass


class EfaFormatNotSupported(Exception):
    pass
