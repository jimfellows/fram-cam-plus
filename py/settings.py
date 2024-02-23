
from PySide6.QtCore import QObject, Slot, Signal, QSortFilterProxyModel, QModelIndex, Property
from PySide6.QtSql import QSqlTableModel, QSqlRecord
from py.logger import Logger
from __feature__ import snake_case  # convert Qt methods to snake


class Settings(QObject):
    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._logger = Logger.get_root()
        self._model = QSqlTableModel(db=db)
        self._model.set_table('FRAM_CAM_SETTINGS')
        # weirdness with getting model to update after db insert is why Im using manualSubmit
        # self._model.set_edit_strategy(QSqlTableModel.OnFieldChange)
        self._model.set_edit_strategy(QSqlTableModel.OnManualSubmit)
        self._model.select()
        self._proxy_model = QSortFilterProxyModel()
        self._proxy_model.set_source_model(self._model)

        self._param_field_pos = self._model.field_index('PARAMETER')
        self._value_field_pos = self._model.field_index('VALUE')

    def _get_value_index(self, parameter):
        """
        Find the position of the value field for a given parameter.
        Using the index we can get or set the param value at the returned address
        :param parameter: str, name of param
        :return: QModelIndex

        TODO: error handling, what to return if something doesnt work out here?
        """
        self._proxy_model.set_filter_key_column(self._param_field_pos)
        self._proxy_model.set_filter_fixed_string(parameter)

        if self._proxy_model.row_count() > 0:
            proxy_ix = self._proxy_model.index(0, self._value_field_pos)
            return self._proxy_model.map_to_source(proxy_ix)

    @Slot(str, result=str)
    def get_param_value(self, parameter, default_value=None):
        """
        retrieve VALUE field associated with matching PARAMETER value
        from table model.  If val doesnt exist yet and we assigna default val,
        put that new value into the table
        :param parameter: str, name of PARAMETER from settings table
        :param default_value: str, if param value is not yet set, set it with this one
        :return:
        """
        value_ix = self._get_value_index(parameter)
        if value_ix:
            return self._model.data(value_ix)
        elif default_value:
            rec = self._model.record()
            rec.set_value(self._param_field_pos, parameter)
            rec.set_value(self._value_field_pos, default_value)
            self._model.insert_record(-1, rec)
            return default_value

    @Slot(str, str, result=bool)
    def set_param_value(self, parameter, value):
        """
        update val in model and db, and create new one if param doesnt yet exist
        :param parameter: str, name of PARAMETER in settings table
        :param value: str, value assigned to VALUE col in settings table
        :return: true/false, depending on success
        """
        value_ix = self._get_value_index(parameter)
        if value_ix:
            result = self._model.set_data(value_ix, value)
        else:
            rec = self._model.record()
            rec.set_value(self._param_field_pos, parameter)
            rec.set_value(self._value_field_pos, value)
            result = self._model.insert_record(-1, rec)

        self._model.submit_all()
        self._logger.info(f"{parameter}={value}, success={result}")
        return result

    @Property(str)
    def vessel_subnet(self):
        return self.get_param_value('Vessel Subnet', default_value='127.0.0')

    @Property(str)
    def backdeck_ip(self):
        return self.vessel_subnet + '.5'

    @Property(str)
    def wheelhouse_ip(self):
        return self.vessel_subnet + '.2'

    @Property(str)
    def ui_theme(self):
        return self.get_param_value('UI Theme', default_value='NOAA')

    @Property(int)
    def cur_haul_id(self):
        haul_id_str = self.get_param_value('Current Haul ID')
        return int(haul_id_str) if haul_id_str else None

    @Property(int)
    def cur_haul_number(self):
        return self.get_param_value('Current Haul Number')

    @Property(int)
    def cur_catch_id(self):
        catch_id_str = self.get_param_value('Current Catch ID')
        return int(catch_id_str) if catch_id_str else None

    @Property(int)
    def cur_catch_display(self):
        return self.get_param_value('Current Catch Display')

    @Property(str)
    def cur_project(self):
        return self.get_param_value('Current Project')

    @Property(str)
    def cur_bio_label(self):
        return self.get_param_value('Current Bio Label')

    @Property(str)
    def cur_specimen_id(self):
        return self.get_param_value('Current Specimen ID')


if __name__ == '__main__':
    print("Running settings")
    from PySide6.QtSql import QSqlDatabase
    from config import LOCAL_DB_PATH
    backdeck_db = QSqlDatabase.add_database('QSQLITE', 'backdeck_db')
    backdeck_db.set_database_name(LOCAL_DB_PATH)
    backdeck_db.open()
    s = Settings(backdeck_db)
    w = s.get_param_value('Wheelhouse Data Directory')
    print(f"Orig dir = {w}")
    w = s.set_param_value('Wheelhouse Data Directory', 'alksjdlaksjdflkj')
    w = s.get_param_value('Wheelhouse Data Directory')
    print(f"New dir = {w}")
    print(s.ui_theme)
    #C:\pycollector\data
    # r = s.get_settings_value('Vessel Subnet Address')

    # print(r)
    # print(w)






