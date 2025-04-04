
# standard imports
import os
import sqlite3

# local imports
from py.config import LOCAL_DB_PATH
from py.logger import Logger

# 3rd party imports
from PySide6.QtCore import QObject
from PySide6.QtSql import QSqlDatabase, QSqlQuery


class QSqlite(QObject):
    """
    class to handle SQLite database objects associated with the
    file path defined during __init__
    """
    def __init__(self, db_path, db_name):
        super().__init__()
        self._logger = Logger.get_root()
        self._db_path = db_path
        self._db = QSqlDatabase.addDatabase('QSQLITE', db_name)
        self._db.setDatabaseName(db_path)
        self._query = None

    @property
    def db(self):
        return self._db

    @property
    def query(self):
        return self._query

    def open_connection(self):
        if self._db.open():
            self._logger.info(f"Successfully opened connection to {self._db_path}")
            return True
        else:
            msg = f"Unable to connect to db: {LOCAL_DB_PATH}"
            self._logger.error(msg)
            return False
    def close_connection(self):
        if self._db.open():
            self._db.close()

    def execute_query(self, sql: str, params=None):
        results = []
        self._query = QSqlQuery(self._db)
        self._query.prepare(sql)

        for k, v in params.items():
            self._query.bindValue(k, v)

        success = self._query.exec()
        if success:
            while self._query.next():
                results.append(self._query.record())
        else:
            self._logger.error(f"Error executing SQL {sql}; {self._db.lastError()}")

        return results

    @staticmethod
    def record_to_dict(r):
        _keys = [r.fieldName(k) for k in range(r.count())]
        _vals = [r.value(k) for k in _keys]
        return dict(zip(_keys, _vals))

    def get_vessel_from_id(self):
        pass


if __name__ == '__main__':
    pass



