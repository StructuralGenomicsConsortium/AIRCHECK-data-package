"""Exception types raised by aircheckdata."""


class AircheckDataError(Exception):
    """Base class for all aircheckdata errors."""


class DatasetNotFoundError(AircheckDataError, ValueError):
    """Raised when a partner or dataset is not present in the dataset registry."""


class DownloadError(AircheckDataError):
    """Raised when a signed URL cannot be obtained or a dataset cannot be downloaded."""
