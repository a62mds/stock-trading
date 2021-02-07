"""
Custom logger.
"""
from datetime import datetime
import logging
from pathlib import Path
from typing import Optional


LOG_DIR: Path = Path(__file__).parent.parent.resolve() / ".logs"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_US = DATETIME_FORMAT + ".%f"
LOGGING_FORMAT = "%(asctime)s|%(levelname)-8s> %(message)s"

# Aliases defined here so that `import logging` isn't needed if this module is imported
debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical
exception = logging.exception

NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class LogSettings(object):
    """
    Dataclass for holding the settings required to set up logging.
    """

    def __init__(self,
        fmt: str=LOGGING_FORMAT,
        console_level: int=WARNING,
        file_level: int=DEBUG,
        directory: Path=LOG_DIR,
        root_name: str=""
    ) -> None:
        """
        Initialize a LogSettings object. Each of the following settings can be specified, but each has a reasonable
        default value:
            - fmt: str
                - Format of log lines
                - Default is "%(asctime)s|%(levelname)-8s> %(message)s"
            - console_level: int
                - Log level of the console logger
                - Default is logging.WARNING
            - file_level: int
                - Log level of the file logger
                - Default is logging.DEBUG
            - directory: Path
                - Directory to write logs into
                - Default is a .logs directory directly under the root directory
            - root_name: str
                - Root of the log file filename
                - Default is ""
        """
        self.fmt: str = fmt
        self.console_level: int = console_level
        self.file_level: int = file_level
        self.directory: Path = directory
        self._root_name: str = root_name
        self._filename: Optional[str] = None
        self._filepath: Optional[Path] = None

    @property
    def filename(self) -> str:
        """
        Getter for the log filename derived from the current date and time, and the root name. If the root name is
        empty, returns a filename of the format YYYY-MM-DDTHH-MM-SS.log; if the root name is nonempty, returns a
        filename of the format YYYY-MM-DDTHH-MM-SS.<root_name>.log.
        """
        if self._filename is None:
            root_name: str = f".{self._root_name}" if self._root_name else self._root_name
            self._filename = f"{datetime.today().strftime('%Y-%m-%dT%H-%M-%S')}{root_name}.log"
        return self._filename

    @property
    def filepath(self) -> Path:
        """
        Getter for the log filepath derived from the directory and the filename.
        """
        if self._filepath is None:
            self._filepath = self.directory / self.filename
        return self._filepath


class Formatter(logging.Formatter):
    """
    Derives from the `logging.Formatter` class to define a custom `formatTime` method.
    From https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format
    """

    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt: str = ""):
        """
        Format the record's (log line's) creation time according to the date format. If non is passed in, use the
        default DATETIME_FORMAT.
        """
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime(DATETIME_FORMAT)
            s = "%s.%03d" % (t, record.msecs)
        return s


def setup(settings: Optional[LogSettings]=None)-> None:
    """
    Set up the logger:
        - Create the log directory
        - Configure the logger
    """
    if settings is None:
        settings = LogSettings()
    to_console("Log filepath: '%s'", str(settings.filepath))
    settings.directory.mkdir(parents=True, exist_ok=True)
    configure(settings.fmt, settings.console_level, settings.file_level, settings.directory / settings.filename)


def configure(fmt: str=LOGGING_FORMAT, console_level: int=WARNING, file_level: int=DEBUG, filepath: "Path"=None) -> None:
    """
    Configure the logger:
        - set the log line format
        - Set the log level of the console logger
        - Set the log level of the file logger
        - Set the filepath for the logs
    """
    logger = logging.getLogger()
    logger.setLevel(DEBUG)
    if not len(logger.handlers):
        formatter = Formatter(fmt)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if filepath is not None:
            file_handler = logging.FileHandler(str(filepath))
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)


def to_console(fmt: str, *args: str) -> None:
    """
    Simulate the logging format but write to console using simple `print` statement.
    """
    timestamp = datetime.now().strftime(DATETIME_FORMAT_US)[:-3]
    message = fmt % tuple(args)
    print(f"{timestamp}|CONSOLE > {message}")
