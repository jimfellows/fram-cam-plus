
from py.logger import Logger
import re

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
            return vessels_dict[int(haul_number[6:9])]
        except (TypeError) as e1:
            LOGGER.error(f"Unable to extract integer ID from haul {haul_number}")
        except KeyError as e2:
            LOGGER.error(f"Vessel ID from haul number {haul_number} not recognized")

    @staticmethod
    def scrub_str_for_file_name(s):
        return re.sub('[^0-9a-zA-Z]+', '', s).lower()





if __name__ == '__main__':
    haul = '202303008001'
    v = Utils.get_vessel_code_from_haul(haul)
    print(v)