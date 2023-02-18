class ServerException(Exception):
    pass

class ParserException(ServerException):
    pass
class UidNotFoundException(ServerException):
    pass
class DuplicateUidException(ServerException):
    pass
class UnauthorizedAccessException(ServerException):
    pass