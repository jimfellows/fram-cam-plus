

from PySide6.QtSql import QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlQuery, QSqlRecord
from PySide6.QtCore import QObject, PyClassProperty, Property, Slot, Signal, QSortFilterProxyModel
from py.logger import Logger
from py.qt_models import FramCamSqlListModel, FramCamFilterableModel, HaulsModel, CatchesModel, ProjectsModel, BiosModel


class FramCamQueryModel(QSqlQueryModel):

    current_index_changed = Signal(int, arguments=['i'])
    py_index_update = Signal(int, arguments=['i'])
    model_loaded = Signal()

    def __init__(self, db):
        super().__init__()
        self._logger = Logger.get_root()
        self._db = db
        self._sql = None
        self._query = QSqlQuery(db)
        self._current_index = -1
        self.model_loaded.connect(self._on_model_loaded)

    def _on_model_loaded(self):
        self._logger.info(f"{self.__class__.__name__} model loaded")
        if self.rowCount() == 1:
            self.set_index_from_py(0)

    @Property(int)
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, i):
        if self._current_index != i:
            self._current_index = i
            self.current_index_changed.emit(i)

    def get_ix_by_value(self, field_name, value):
        for i in range(0, self.rowCount()):
            if value == self.record(i).value(field_name):
                return i

        return -1

    def set_index_from_py(self, i):
        print(f"Emitting index {i} to qml")
        self.py_index_update.emit(i)

    @property
    def row_count(self):
        return self.rowCount()


    @Slot(int, str, result="QVariant")
    def getRowValue(self, i, col_name):
        """
        Slot for qml to retrieve value given index and col name.
        model.record(i).value(name) doesnt appear to work as a slot
        directly from QSQLQueryModel, so this wrapper fills that need

        TODO: is this hitting the db or memory?

        :param i: row/model index
        :param col_name: name of column (Is this case sensitive?)
        :return: int/str/db type val
        """
        return self.record(i).value(col_name)


class HaulsModelV1(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = 'select * from fram_cam_hauls order by cast(haul_number as bigint) desc'
        self.loadModel()

class CatchOptionsModel(FramCamQueryModel):
    def __init__(self, db):
        super().__init__(db)
        self._sql  = '''
            select      display_name
                        ,catch_id
            from        catch
            where       operation_id = :operation_id
                        and receptacle_seq is null
            order by    display_name
        '''

    @Slot(int, name="populate")
    def populate(self, operation_id):
        self.clear()
        self._query.prepare(self._sql)
        self._query.bindValue(':operation_id', operation_id)
        self._query.exec()
        self.setQuery(self._query)
        self.model_loaded.emit()

class ProjectOptionsModel(FramCamQueryModel):

    def __init__(self, db):
        super().__init__(db)
        self._sql = '''
            select      distinct
                        sp.plan_name as project
            from        specimen s
            join        species_sampling_plan_lu sp
                        on s.species_sampling_plan_id = sp.species_sampling_plan_id
            where       catch_id = :catch_id
                        and s.parent_specimen_id is not null
            order by    case when sp.plan_name = 'FRAM Standard Survey' then -1 else 0 end
                        ,plan_name
        '''

    @Slot(int, name="populate")
    def populate(self, catch_id):
        self.clear()
        self._query.prepare(self._sql)
        self._query.bindValue(':catch_id', catch_id)
        self._query.exec()
        self.setQuery(self._query)
        self.model_loaded.emit()

    @property
    def cur_project(self):
        return self.getRowValue(self._current_index, 'PLAN_NAME')

class BioOptionsModel(FramCamQueryModel):
    def __init__(self, db):
        super().__init__(db)
        self._sql = '''
            select
                        coalesce(alpha_value, cast(cast(numeric_value as int) as text)) || ' - ' || coalesce(tl.subtype, tl.type) as display
                        ,coalesce(alpha_value, cast(cast(numeric_value as int) as text)) as bio_label
                        ,specimen_id
                        ,parent_specimen_id
            from        specimen s
            join        species_sampling_Plan_lu sp
                        on s.species_sampling_plan_id = sp.species_sampling_plan_id
            join        types_lu tl
                        on s.action_type_id = tl.type_id
            where       catch_id = :catch_id
                        and coalesce(:plan_name, sp.plan_name) = sp.plan_name
                        and tl.type like '%ID'
            order by    tl.type
                        ,tl.subtype
                        ,coalesce(alpha_value, numeric_value)
        '''
        # self.setHeaderData(0, not Qt)

    # overloaded slot with two decorators for optional param
    @Slot(int, name="populate")
    @Slot(int, "QVariant", name="populate")
    def populate(self, catch_id, plan_name=None):
        self.clear()
        self._query.prepare(self._sql)
        self._query.bindValue(':catch_id', catch_id)
        self._query.bindValue(':plan_name', plan_name)
        self._query.exec()
        self.setQuery(self._query)
        self.model_loaded.emit()


class SpecimensModel(QSqlQueryModel):
    def __init__(self, db):
        super().__init__()
        self._query = QSqlQuery(db)
        self._query.prepare('''
            select
                        haul_number
                        ,h.vessel_name
                        ,h.station_code
                        ,h.latitude_min
                        ,h.latitude_max
                        ,h.longitude_min
                        ,h.longitude_max
                        ,c.catch_id
                        ,c.display_name
                        ,tx.common_name_1 as common_name
                        ,tx.scientific_name
                        ,sp.plan_name
                        ,s.specimen_id
                        ,sc.specimen_id as specimen_bio_id
                        ,t.type as action_type
                        ,t.subtype as action_subtype
                        ,coalesce(sc.alpha_value, cast(sc.numeric_value as text)) as bio_label
            from        hauls h
            left join   catch c
                        on h.haul_id = c.operation_id
                        and c.receptacle_seq is null
                        and c.display_name not like 'Mix%'
            left join   catch_content_lu cc
                        on c.catch_content_id = cc.catch_content_id
            left join   taxonomy_lu tx
                        on cc.taxonomy_id = tx.taxonomy_id
            left join   specimen s
                        on c.catch_id = s.catch_id
            left join   specimen sc
                        on s.specimen_id = sc.parent_specimen_id
            left join   types_lu t
                        on t.type_id = sc.action_type_id
            left join   species_sampling_plan_lu sp
                        on sc.species_sampling_plan_id = sp.species_sampling_plan_id
            order by    cast(haul_number as bigint)
        ''')
        self._query.exec_()
        self.setQuery(self._query)


class DataSelector(QObject):
    unusedSignal = Signal()
    haulIndexReset = Signal(int, arguments=['i'])

    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._logger = Logger.get_root()

        # setup hauls model
        # TODO: proxy models for in memory sorting?
        self._hauls_model = HaulsModel(db)
        self._hauls_model.loadModel()
        self._catches_model = CatchesModel(db)
        self._catches_proxy = FramCamFilterableModel(self._catches_model)
        self._projects_model = ProjectsModel(db)
        self._projects_proxy = FramCamFilterableModel(self._projects_model)
        self._bios_model = BiosModel(db)
        self._bios_proxy = FramCamFilterableModel(self._bios_model)

        # when haul changes populate the other models
        self._hauls_model.currentIndexChanged.connect(lambda i: self._on_haul_changed(i))
        self._catches_model.currentIndexChanged.connect(lambda i: self._on_catch_changed(i))
        self._projects_model.currentIndexChanged.connect(lambda i: self._on_project_changed(i))
        self._bios_model.currentIndexChanged.connect(lambda i: self._on_bio_changed(i))

        """
        Below we select model rows pulled from database on startup.  Note that we set _current_index, not
        current_index to avoid signaling to UI directly.  We use this backchannel because...
        """
        # if we have pre-selected vals from db, set them now, in order (haul,catch,project,bio)
        # _haul_model_ix = self._hauls_model.get_ix_by_value('HAUL_ID', self._app.state.cur_haul_id)
        # self._hauls_model._current_index = _haul_model_ix
        # self._on_haul_changed(_haul_model_ix)

        # _catch_model_ix = self._catches_model.get_ix_by_value('CATCH_ID', self._app.state.cur_catch_id)
        # self._catches_model._current_index = _catch_model_ix
        # self._on_catch_changed(_catch_model_ix)
        #
        # _projects_model_ix = self._projects_model.get_ix_by_value('PROJECT', self._app.state.cur_project)
        # self._projects_model._current_index = _projects_model_ix
        # self._on_project_changed(_projects_model_ix)
        #
        # _bios_model_ix = self._bios_model.get_ix_by_value('BIO_LABEL', self._app.state.cur_bio_label)
        # self._bios_model._current_index = _bios_model_ix
        # self._on_bio_changed(_bios_model_ix)


    def _get_haul_ix_by_id_v2(self, haul_id):
        """
        Find the position of the value field for a given parameter.
        Using the index we can get or set the param value at the returned address
        :param parameter: str, name of param
        :return: QModelIndex

        TODO: error handling, what to return if something doesnt work out here?
        """
        haul_field_ix = 0#self._hauls_model.field_index('HAUL_ID')
        self._hauls_proxy_model.set_filter_key_column(haul_field_ix)
        self._hauls_proxy_model.set_filter_fixed_string(haul_id)

        if self._hauls_proxy_model.row_count() > 0:
            proxy_ix = self._hauls_proxy_model.index(0, haul_field_ix)
            return self._hauls_proxy_model.map_to_source(proxy_ix)[0]

    def _on_haul_changed(self, new_haul_index):
        print(f"New haul changed to {new_haul_index}")
        # TODO: set cur haul id here?
        self._cur_haul_rec = self._hauls_model.getItem(new_haul_index)
        self._catches_model.setBindParam(':fram_cam_haul_id', self._cur_haul_rec['fram_cam_haul_id'])
        self._catches_model.setBindParam(':fram_cam_haul_id', self._cur_haul_rec['fram_cam_haul_id'])
        self._catches_model.loadModel()
        self._projects_model.clearModel()
        self._bios_model.clearModel()

    def _on_catch_changed(self, new_catch_index):
        """
        things to do when user changes the drop down for catch options.
        :param new_catch_index: new model index
        :return:
        """
        self._cur_catch_rec = self._catches_model.getItem(new_catch_index)
        # self._logger.info(f"Selected catch changed to {self._cur_catch_id}")
        self._projects_model.setBindParam(':fram_cam_haul_id', self._cur_catch_rec['fram_cam_haul_id'])
        self._projects_model.loadModel()
        self._projects_proxy.filterOnStrRole('display_name', self._cur_catch_rec['display_name'])
        self._bios_model.setBindParam(':fram_cam_haul_id', self._cur_catch_rec['fram_cam_haul_id'])
        self._bios_model.loadModel()
        self._bios_proxy.filterOnStrRole('display_name', self._cur_catch_rec['display_name'])

        self._app.state.set_state_value('Current Catch ID', self._cur_catch_rec['fram_cam_catch_id'])
        self._app.state.set_state_value('Current Catch Display', self._cur_catch_rec['display_name'])

    def _on_project_changed(self, new_project_index):
        self._cur_project_rec = self._projects_model.getItem(new_project_index)
        # self._logger.info(f"Selected project changed to {self._cur_project_name}")
        self._bios_proxy.filterOnStrRole('project_name', self._cur_project_rec['project_name'])
        self._app.state.set_state_value('Current Project', self._cur_project_rec['project_name'])

    def _on_bio_changed(self, new_bio_index):
        self._cur_bio_rec = self._bios_model.getItem(new_bio_index)
        # self._logger.info(f"Selected bio label changed to {self._cur_bio_label}")
        self._app.state.set_state_value('Current Bio Label', self._cur_bio_rec['bio_label'])

    @Property(QObject, notify=unusedSignal)
    def hauls_model(self):
        return self._hauls_model

    def get_haul_num_from_id(self, haul_id):
        return self._hauls_model.record()

    @Property(QObject, notify=unusedSignal)
    def catches_model(self):
        return self._catches_model

    @Property(QObject, notify=unusedSignal)
    def catches_proxy(self):
        return self._catches_proxy

    @Property(QObject, notify=unusedSignal)
    def projects_model(self):
        return self._projects_model

    @Property(QObject, notify=unusedSignal)
    def projects_proxy(self):
        return self._projects_proxy

    @Property(QObject, notify=unusedSignal)
    def bios_model(self):
        return self._bios_model

    @Property(QObject, notify=unusedSignal)
    def bios_proxy(self):
        return self._bios_proxy

    # def _set_cur_haul_number(self):
    #     self._current_haul_number = self._hauls_model.getRowValue(self._h)
