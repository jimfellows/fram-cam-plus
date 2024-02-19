

from PySide6.QtSql import QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlQuery, QSqlRecord
from PySide6.QtCore import QObject, PyClassProperty, Property, Slot, Signal
from py.logger import Logger


class FramCamQueryModel(QSqlQueryModel):

    current_index_changed = Signal(int, arguments=['i'])

    def __init__(self, db):
        super().__init__()
        self._logger = Logger.get_root()
        self._db = db
        self._sql = None
        self._query = QSqlQuery(db)
        self._current_index = -1

    @Property(int)
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, i):
        if self._current_index != i:
            self._current_index = i
            self.current_index_changed.emit(i)

    @Slot(int, str, name='getRowValue', result="QVariant")
    def getRowValue(self, i, col_name):
        """
        Slot for qml to retrieve value given index and col name.
        model.record(i).value(name) doesnt appear to work as a slot
        directly from QSQLQueryModel, so this wrapper fills that need
        :param i: row/model index
        :param col_name: name of column (Is this case sensitive?)
        :return: int/str/db type val
        """
        return self.record(i).value(col_name)


class HaulsModel(FramCamQueryModel):
    def __init__(self, db):
        super().__init__(db)
        self._logger = Logger.get_root()
        self._sql = '''
            select
                        haul_number
                        ,haul_id
                        ,vessel_name
                        ,station_code
                        ,latitude_min
                        ,latitude_max
                        ,longitude_min
                        ,longitude_max
            from        hauls
            order by    cast(haul_number as bigint) desc
        '''
        self.populate()

    @Slot(name='populate')
    def populate(self):
        self.clear()
        self._query.prepare(self._sql)
        self._query.exec()
        self.setQuery(self._query)

    @property
    def cur_haul_number(self):
        return self.getRowValue(self._current_index, 'HAUL_NUMBER')

    @property
    def cur_haul_id(self):
        return self.getRowValue(self._current_index, 'HAUL_ID')


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

    @property
    def cur_catch_id(self):
        return self.getRowValue(self._current_index, 'CATCH_ID')


class ProjectOptionsModel(FramCamQueryModel):

    def __init__(self, db):
        super().__init__(db)
        self._sql = '''
            select      distinct
                        sp.plan_name
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

    @property
    def cur_project(self):
        return self.getRowValue(self._current_index, 'PLAN_NAME')

class BioOptionsModel(FramCamQueryModel):
    def __init__(self, db):
        super().__init__(db)
        self._sql = '''
            select
                        coalesce(alpha_value, floor(numeric_value)) || ' - ' || coalesce(tl.subtype, tl.type) as display
                        ,coalesce(alpha_value, floor(numeric_value)) as bio_label
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
    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._logger = Logger.get_root()
        self._hauls_model = HaulsModel(db)
        self._catch_options_model = CatchOptionsModel(db)
        self._project_options_model = ProjectOptionsModel(db)
        self._bio_options_model = BioOptionsModel(db)

        # wanted to handle this within each model, but weird race conditions happening...
        self._cur_haul_id = None
        self._cur_catch_id = None
        self._cur_project = None
        self._cur_bio_label = None

        # when haul changes populate the other models
        self._hauls_model.current_index_changed.connect(lambda i: self._handle_changed_haul(i))
        self._catch_options_model.current_index_changed.connect(lambda i: self._handle_changed_catch(i))
        self._project_options_model.current_index_changed.connect(lambda i: self._handle_changed_project(i))

    def _handle_changed_haul(self, new_haul_index):
        # TODO: set cur haul id here?
        self._cur_haul_id = self._hauls_model.getRowValue(new_haul_index, 'HAUL_ID')
        self._logger.info(f"Selected haul id changed to {self._cur_haul_id}")
        self._catch_options_model.populate(self._cur_haul_id)
        self._project_options_model.clear()
        self._bio_options_model.clear()
        self._app.settings.set_param_value('Current Haul ID', self._cur_haul_id)

    def _handle_changed_catch(self, new_catch_index):
        """
        things to do when user changes the drop down for catch options.
        :param new_catch_index: new model index
        :return:
        """
        self._cur_catch_id = self._catch_options_model.getRowValue(new_catch_index, 'CATCH_ID')
        self._logger.info(f"Selected catch changed to {self._cur_catch_id}")
        self._project_options_model.populate(self._cur_catch_id)
        self._bio_options_model.populate(self._cur_catch_id)
        self._app.settings.set_param_value('Current Catch ID', self._cur_catch_id)

    def _handle_changed_project(self, new_project_index):
        self._cur_project_name = self._project_options_model.getRowValue(new_project_index, 'PLAN_NAME')
        self._logger.info(f"Selected project changed to {self._cur_project_name}")
        self._bio_options_model.populate(self._cur_catch_id, self._cur_project_name)
        self._app.settings.set_param_value('Current Project', self._cur_project_name)

    @Property(QObject)
    def hauls_model(self):
        return self._hauls_model

    @Property(QObject)
    def catch_options_model(self):
        return self._catch_options_model

    @Property(QObject)
    def project_options_model(self):
        return self._project_options_model

    @Property(QObject)
    def bio_options_model(self):
        return self._bio_options_model

    # def _set_cur_haul_number(self):
    #     self._current_haul_number = self._hauls_model.getRowValue(self._h)
