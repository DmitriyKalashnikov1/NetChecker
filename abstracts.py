import abc
from pathlib import Path
from NetCheckExceptions import *


# With this abstract classes we can use any needed python lib inside them but we always have same API for main app

# base class for txt-files database
class DataBase(abc.ABC):
    _PATH = Path("")

    _data = []

    exceptIfDBDataNotValid = False

    def __init__(self, path_to_base: str, exceptIfNotValid=False):
        self._PATH = Path(path_to_base)
        self.exceptIfDBDataNotValid = exceptIfNotValid

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        raise DBNotModifycateable

    def addToBase(self, source: list):
        self._data += source

    @abc.abstractmethod
    def read(self):
        "Read the file"

    @abc.abstractmethod
    def write(self, data: list):
        "Write data to file"

    @abc.abstractmethod
    def check(self):
        "Check file valid"


# base class for ipchecker
class IPChecker(abc.ABC):
    servers = []
    db_check_res = []
    debug = False
    server_info = []
    result_of_testing = []

    def __init__(self, debug=False):
        self.debug = debug

    @abc.abstractmethod
    def read_from_dataBase(self, dbase: DataBase):
        "upload to checker what to check"

    @abc.abstractmethod
    def check_all(self):
        "check"

    @abc.abstractmethod
    def show_check_result(self):
        "show check result"


# base class for main app
class NetChecker(abc.ABC):
    ipchecker = None
    db = None

    def __init__(self, db: DataBase, checker: IPChecker):
        self.db = db
        self.ipchecker = checker

    @abc.abstractmethod
    def checkAndPrepareEnv(self):
        "Check PC env"

    def run(self):
        self.ipchecker.read_from_dataBase(self.db)
        self.ipchecker.check_all()
        self.ipchecker.show_check_result()
