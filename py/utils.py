
from py.logger import Logger
import re
from PySide6.QtSql import QSqlRecord

LOGGER = Logger.get_root()

class Utils:

    @staticmethod
    def get_vessel_code_from_haul(haul_number):
        vessels_dict = {
            8: 'EX',
            10: 'MJ',
            17: 'NA',
            20: 'LS'
        }
        try:
            if 't' in haul_number.lower():
                return 'TT'

            return vessels_dict[int(haul_number[6:9])]
        except (TypeError) as e1:
            LOGGER.error(f"Unable to extract integer ID from haul {haul_number}")
        except KeyError as e2:
            LOGGER.error(f"Vessel ID from haul number {haul_number} not recognized")

    @staticmethod
    def scrub_str_for_file_name(s):
        return re.sub('[^0-9a-zA-Z]+', '', s).lower()

    @staticmethod
    def qrec_to_dict(rec: QSqlRecord):
        """
        covert a QSQLrecord instances to a python dict.  Use me to append records to self._records
        :param rec: QSqlRecord
        :return: dictionary
        """
        _keys = [rec.fieldName(k).lower() for k in range(rec.count())]
        _vals = [rec.value(k) for k in _keys]
        return dict(zip(_keys, _vals))


if __name__ == '__main__':
    haul = '202303008001'
    v = Utils.get_vessel_code_from_haul(haul)
    print(v)