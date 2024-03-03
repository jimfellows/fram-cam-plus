

from PySide6.QtSql import QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlQuery, QSqlRecord
from PySide6.QtCore import QObject, PyClassProperty, Property, Slot, Signal, QSortFilterProxyModel
from py.logger import Logger
from py.qt_models import FramCamSqlListModel, FramCamFilterProxyModel, HaulsModel, CatchesModel, ProjectsModel, BiosModel


class DataSelector(QObject):
    unusedSignal = Signal()
    haulIndexReset = Signal(int, arguments=['i'])

    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._logger = Logger.get_root()

        # setup hauls model
        self._hauls_model = HaulsModel(db)
        self._hauls_model.loadModel()
        self._catches_model = CatchesModel(db)
        self._projects_model = ProjectsModel(db)
        self._bios_model = BiosModel(db)

        # proxy models will allow us to filter further based on upstream selections
        self._catches_proxy = FramCamFilterProxyModel(self._catches_model)
        self._projects_proxy = FramCamFilterProxyModel(self._projects_model)
        self._bios_proxy = FramCamFilterProxyModel(self._bios_model)

        # when haul changes populate the other models
        self._hauls_model.currentIndexChanged.connect(lambda i: self._on_haul_changed(i))
        self._catches_model.currentIndexChanged.connect(lambda i: self._on_catch_changed(i))
        self._projects_model.currentIndexChanged.connect(lambda i: self._on_project_changed(i))
        self._bios_model.currentIndexChanged.connect(lambda i: self._on_bio_changed(i))

        """
        Below we select model rows pulled from database on startup.  Note that we set _current_index, not
        current_index to avoid signaling to UI directly.  We use this backchannel because QML items will not exist yet
        since we initialize python items first.  currentIndexChanged signal wont be caught, hence the manual call to
        _on_haul_changed/catch/project/bio.
        """
        # if we have pre-selected vals from db, set them now, in order (haul,catch,project,bio)
        if self._app.state.cur_haul_id:
            _haul_model_ix = self._hauls_model.getRowIndexByValue('fram_cam_haul_id', self._app.state.cur_haul_id)
            self._logger.info(f"Setting initial HaulsModel row to {_haul_model_ix}, fram_cam_haul_id={self._app.state.cur_haul_id}")
            self._hauls_model._current_index = _haul_model_ix
            self._on_haul_changed(_haul_model_ix)

        if self._app.state.cur_catch_id:
            _catch_model_ix = self._catches_model.getRowIndexByValue('fram_cam_catch_id', self._app.state.cur_catch_id)
            self._logger.info(f"Setting initial CatchesModel row to {_catch_model_ix},  fram_cam_catch_id={self._app.state.cur_catch_id}")
            self._catches_model._current_index = _catch_model_ix
            self._on_catch_changed(_catch_model_ix)

        if self._app.state.cur_project:
            _projects_model_ix = self._projects_model.getRowIndexByValue('project_name', self._app.state.cur_project)
            self._logger.info(f"Setting initial ProjectsModel row to {_projects_model_ix}, project {self._app.state.cur_project}")
            self._projects_model._current_index = _projects_model_ix
            self._on_project_changed(_projects_model_ix)

        if self._app.state.cur_bio_label:
            _bios_model_ix = self._bios_model.getRowIndexByValue('bio_label', self._app.state.cur_bio_label)
            self._logger.info(f"Setting initial BiosModel row to {_bios_model_ix}, bio_label {self._app.state.cur_bio_label}")
            self._bios_model._current_index = _bios_model_ix
            self._on_bio_changed(_bios_model_ix)

    def _on_haul_changed(self, new_haul_index):
        # TODO: set cur haul id here?
        self._cur_haul_rec = self._hauls_model.getItem(new_haul_index)

        self._catches_model.setBindParam(':fram_cam_haul_id', self._cur_haul_rec['fram_cam_haul_id'])
        self._projects_model.setBindParam(':fram_cam_haul_id', self._cur_haul_rec['fram_cam_haul_id'])
        self._bios_model.setBindParam(':fram_cam_haul_id', self._cur_haul_rec['fram_cam_haul_id'])

        self._catches_model.loadModel()
        self._projects_model.loadModel()
        self._bios_model.loadModel()

        self._app.state.set_state_value('Current Haul Number', self._cur_haul_rec['haul_number'])
        self._app.state.set_state_value('Current Haul ID', self._cur_haul_rec['fram_cam_haul_id'])

    def _on_catch_changed(self, new_catch_index):
        """
        things to do when user changes the drop down for catch options.
        :param new_catch_index: new model index
        :return:
        """
        self._cur_catch_rec = self._catches_model.getItem(new_catch_index)
        self._logger.info(f"Selected catch changed to {self._cur_catch_rec['display_name']}")
        self._projects_proxy.filterRoleOnStr('display_name', self._cur_catch_rec['display_name'])
        self._bios_proxy.filterRoleOnRegex('bio_filter_str', f'"display_name":"{self._cur_catch_rec['display_name']}"')
        self._app.state.set_state_value('Current Catch ID', self._cur_catch_rec['fram_cam_catch_id'])
        self._app.state.set_state_value('Current Catch Display', self._cur_catch_rec['display_name'])

    def _on_project_changed(self, new_project_index):
        self._cur_project_rec = self._projects_model.getItem(new_project_index)
        self._logger.info(f"Selected project changed to {self._cur_project_rec['project_name']}")
        _regex = f'"display_name":"{self._cur_catch_rec['display_name']}","project_name":"{self._cur_project_rec['project_name']}"'
        self._bios_proxy.filterRoleOnRegex('bio_filter_str', _regex)
        self._app.state.set_state_value('Current Project', self._cur_project_rec['project_name'])

    def _on_bio_changed(self, new_bio_index):
        self._cur_bio_rec = self._bios_model.getItem(new_bio_index)
        self._logger.info(f"Selected bio label changed to {self._cur_bio_rec['bio_label']}")
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
