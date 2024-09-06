# -*- coding: utf-8 -*-
import json
import sqlite3
import time
from abc import abstractclassmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import CHRLINE


def ezLocker(func):
    def check(*args, **kwargs):
        if args[0]._checkLock():
            return func(*args, **kwargs)
        else:
            raise Exception("can't use Timeline func")

    return check


class BaseDatabase:
    _LOG_KEY = "BASE"

    def __init__(self, cl: "CHRLINE", db_name: Optional[str]):
        self.cl = cl
        if db_name is None:
            db_name = self.cl.mid
        self.db_name = db_name
        self.__logger = self.cl.get_logger("DB")
        self.logger = self.__logger.overload(self._LOG_KEY)
        self.logger.info("Initialize database...")
        self._ezLocker = False
        self.loadDatabase()

    @abstractclassmethod
    def loadDatabase(self):
        raise NotImplementedError

    def _lock(self):
        self._ezLocker = True

    def _lockRrelease(self):
        self._ezLocker = False

    def _checkLock(self):
        while self._ezLocker:
            time.sleep(1 / 1000)
        return True


class SqliteDatabase(BaseDatabase):
    _LOG_KEY = "SQLite"

    def loadDatabase(self):
        self.logger.info(f"Loading `db_{self.db_name}` with Sqli")
        path = self.cl.getCacheData(".database", f"{self.db_name}.db", pathOnly=True)
        if path:
            self._sqlite = sqlite3.connect(path)
        if self._sqlite:
            self._init()
        else:
            raise Exception("can not load database.")

    @ezLocker
    def getData(self, _key, _defVal=None):
        SQLITE3_SELECT_CMD = """ SELECT * FROM [CHRLINE] WHERE [key]=?; """
        cursor = self._sqlite.cursor()
        cursor.execute(SQLITE3_SELECT_CMD, (_key,))
        rows = cursor.fetchone()
        cursor.close()
        return _defVal if not rows else self._val2obj(rows[2])

    def saveData(self, _key, _val):
        SQLITE3_SAVE_DATA_CMD = """
            INSERT OR REPLACE INTO [CHRLINE] ([key], [val]) values (?, ?); 
        """
        cursor = self._sqlite.cursor()
        cursor.execute(SQLITE3_SAVE_DATA_CMD, (_key, self._obj2val(_val)))
        self.saveDatabase()
        cursor.close()

    def saveDatabase(self):
        self._sqlite.commit()

    def _obj2val(self, obj):
        a = type(obj)
        if a in [list, dict]:
            return json.dumps(obj)
        elif a in [str, int]:
            return str(obj)
        raise ValueError(f"can not conv data type to string: {a} -> {obj}")

    def _val2obj(self, val):
        # TODO: check and reload with json.loads if it is json data
        try:
            val = json.loads(val)
        except Exception as _:
            self.logger.warning(f"[_val2obj] cant conv data for json: {val}")
        return val

    def _init(self):
        SQLITE3_CHRLINE_UNIT_TABLE_CMD = """
            CREATE TABLE IF NOT EXISTS CHRLINE (
                id integer PRIMARY KEY,
                key text NOT NULL UNIQUE,
                val text
            );
        """
        cursor = self._sqlite.cursor()
        cursor.execute(SQLITE3_CHRLINE_UNIT_TABLE_CMD)
        cursor.close()


class JsonDatabase(BaseDatabase):
    _LOG_KEY = "JSON"

    def loadDatabase(self):
        self.logger.info(f"Loading `db_{self.db_name}` with Json")
        _data = self.cl.getCacheData(".database", f"{self.db_name}.json")
        self._json = json.loads(_data) if _data is not None and _data != "" else {}

    def getData(self, _key, _defVal=None):
        return self._json.get(_key, _defVal)

    def saveData(self, _key, _val):
        self._json[_key] = _val
        self.saveDatabase()

    def saveDatabase(self):
        self.cl.saveCacheData(
            ".database", f"{self.db_name}.json", json.dumps(self._json)
        )
        self.logger.info(f"Save `db_{self.db_name}` with Json success")
