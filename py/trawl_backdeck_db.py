

import os
import sqlite3

from config import LOCAL_DB_PATH
from PySide6.QtCore import QObject
from PySide6.QtSql import QSqlDatabase
from py.logger import Logger


class BackdeckDB(QObject):
    def __init__(self, db_path, db_name):
        super().__init__()
        self._logger = Logger.get_root()
        self._db_path = db_path
        self._db = QSqlDatabase.addDatabase('QSQLITE', db_name)
        self._db.setDatabaseName(db_path)



    def open_connection(self):
        if self._db.open():
            self._logger.info(f"Successfully opened connection to {self._db_path}")
        else:
            msg = f"Unable to connect to local db: {LOCAL_DB_PATH}"
            self._logger.error(msg)
            raise Exception(msg)


logger = Logger.get_root()
backdeck_db = QSqlDatabase.addDatabase('QSQLITE', 'localdb')
backdeck_db.setDatabaseName(LOCAL_DB_PATH)
if backdeck_db.open():
    logger.info(f"Successfully connected to {backdeck_db.databaseName()}")
else:
    msg = f"Unable to connect to local db: {backdeck_db.databaseName()}"
    logger.error(msg)
    raise Exception(msg)

#
# def open_connection(self):
#     if self._db.open():
#         self._logger.info(f"Successfully opened connection to {self._db_path}")
#     else:
#         msg = f"Unable to connect to local db: {LOCAL_DB_PATH}"
#         self._logger.error(msg)
#         raise Exception(msg)
#
#
#
# class TrawlBackdeckDB(QSqlDatabase):
#
#     def __init__(self, db_path, db_name):
#         super().__init__()
#         self._logger = Logger.get_root()
#         self._db_path = db_path
#         self._db = self.addDatabase('QSQLITE', db_name)
#         # self._db.setDatabaseName(db_path)
#
#     def open_connection(self):
#         if self._db.open():
#            self._logger.info(f"Successfully opened connection to {self._db_path}")
#         else:
#             msg = f"Unable to connect to local db: {LOCAL_DB_PATH}"
#             self._logger.error(msg)
#             raise Exception(msg)




# class TrawlBackdeckDB:
#
#     def __init__(self):
#         self._logger = Logger().get_root()
#         self._db_path = None
#         self._con = None
#         # self._set_db_path()
#         self._create_connection()
#
#     # def _set_db_path(self):
#     #     expected_path = os.path.join(DATA_DIR, 'trawl_backdeck.db')
#     #     if os.path.exists(expected_path):
#     #         self._db_path = expected_path
#     #     else:
#     #         self._logger.error(f"Unable to location trawl backdeck db at {expected_path}")
#     #         self._db_path = None
#
#     def _dict_factory_v1(self, cursor, row):
#         """
#         row factory optimized to return k:v pairs for query results.
#         See: https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
#         """
#         d = {}
#         for idx, col in enumerate(cursor.description):
#             d[col[0]] = row[idx]
#         return d
#
#     def _dict_factory_v2(self, cursor, row):
#         """
#         row factory optimized to return k:v pairs for query results.
#         See: https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
#         """
#         fields = [column[0] for column in cursor.description]
#         return {key: value for key, value in zip(fields, row)}
#
#     def _create_connection(self):
#         self._logger.info(f"Connecting to trawl_backdeck.db at {DB_PATH}")
#         if os.path.exists(DB_PATH):
#             self._con = sqlite3.connect(DB_PATH)
#             self._con.row_factory = self._dict_factory_v2
#
#     def execute_query(self, sql, params=()):
#         return self._con.execute(sql, params)
#
#     def get_hauls(self):
#         return self._con.execute('select * from hauls')
#
#     def get_all_catches(self):
#         return self._con.execute('select * from catches where receptacle_seq is null')
#
#     def get_catches_for_haul(self, haul_num):
#         return self._con.execute('''
#                 select
#                             c.*
#                 from        catch c
#                 join        hauls h
#                             on c.operation_id = h.haul_id
#                 where       h.haul_number = ?
#             ''',
#             (haul_num,)
#         )
#
#
#
#
# if __name__ == '__main__':
#     tbdb = TrawlBackdeckDB()
#     hauls = tbdb.execute_query('select count(*) as ct from hauls')
#     for h in tbdb.get_hauls():
#         # print(h)
#         pass
#     for c in tbdb.get_catches_for_haul('202303008001'):
#         print(c)