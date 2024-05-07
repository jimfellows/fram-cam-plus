

from PySide6.QtSql import QSqlQueryModel, QSqlTableModel, QSqlRelation, QSqlQuery, QSqlRecord
from PySide6.QtCore import QObject, PyClassProperty, Property, Slot, Signal, QSortFilterProxyModel, QThread
from py.logger import Logger
from py.qt_models import FramCamSqlListModel, FramCamFilterProxyModel, HaulsModel, CatchesModel, ProjectsModel, BiosModel
from datetime import datetime

from py.qsqlite import QSqlite
import socket
from xmlrpc import client as xrc


class GetBackdeckBiosWorker(QObject):
    """
    call to backdeck rpc server to retrieve data from backdeck sqlite db.
    Idea here is this goes to work whenever user requests new data from the backdeck software, which
    has an RPC server spinning at a particular ip/port.

    Function will return
        1.) a list of all hauls
        2a.) catch/bios for the most recent haul
        2b.) catch/bios for the specified haul, if different from the most recent

    Should allow the app to always have all tows, but only pull catch data for the desired tow of interest
    """

    backdeckResults = Signal(bool, str, int, arguments=['status', 'msg', 'rowsRetrieved'])
    pullComplete = Signal()

    def __init__(self, app=None, db=None):
        super().__init__()
        self._logger = Logger.get_root()
        self._app = app

        self._hauls_table_model = QSqlTableModel(db=db)
        self._hauls_table_model.setTable('BACKDECK_HAULS_LOG')
        self._hauls_table_model.setEditStrategy(QSqlTableModel.OnManualSubmit)

        self._bio_table_model = QSqlTableModel(db=db)
        self._bio_table_model.setTable('BACKDECK_BIOS_LOG')
        self._bio_table_model.setEditStrategy(QSqlTableModel.OnManualSubmit)

        self._cur_haul_num = None

    @property
    def cur_haul_num(self):
        return self._cur_haul_num

    @cur_haul_num.setter
    def cur_haul_num(self, haul_num):
        self._cur_haul_num = haul_num

    def run(self):
        """
        Get data from backdeck and append to log-style table.  Signal emitted should be
        picked up to notify UI/app that we have new data
        :return:
        """
        _success = False
        _msg = ''
        _bios = []
        _backdeck_address = f'http://{self._app.settings.curBackdeckIp}:{self._app.settings.curBackdeckRpcPort}'

        self._logger.debug(f"Retrieving new data from backdeck at {_backdeck_address}")
        try:
            try:
                _server = xrc.ServerProxy(_backdeck_address, allow_none=True, use_builtin_types=True)
                _bios = _server.get_backdeck_bios(self._cur_haul_num)
            except Exception as ex:
                _msg = 'Error contacting backdeck computer: ' + str(ex)
                self._logger.error(_msg)
                return

            try:
                for _b in [x for x in _bios]:
                    _bio_rec = self._bio_table_model.record()
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('BACKDECK_CLIENT_NAME'), _b['BACKDECK_CLIENT_NAME'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('HAUL_NUMBER'), _b['HAUL_NUMBER'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('DISPLAY_NAME'), _b['DISPLAY_NAME'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('COMMON_NAME'), _b['COMMON_NAME'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('SCIENTIFIC_NAME'), _b['SCIENTIFIC_NAME'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('BIO_LABEL'), _b['BIO_LABEL'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('BIO_TYPE'), _b['BIO_TYPE'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('BIO_SUBTYPE'), _b['BIO_SUBTYPE'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('PROJECT_NAME'), _b['PROJECT_NAME'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('PROJECT_SCIENTIST'), _b['PROJECT_SCIENTIST'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('INSERTED_DT'), datetime.now().isoformat(timespec="milliseconds"))
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('HAUL_ID'), _b['HAUL_ID'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('CATCH_ID'), _b['CATCH_ID'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('SPECIMEN_ID'), _b['SPECIMEN_ID'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('SPECIMEN_ATTR_ID'), _b['SPECIMEN_ATTR_ID'])
                    _bio_rec.setValue(self._bio_table_model.fieldIndex('TAXONOMY_ID'), _b['TAXONOMY_ID'])

                    self._bio_table_model.insertRecord(-1, _bio_rec)
                    self._bio_table_model.submitAll()

                self._logger.info(f"Retrieved and inserted {len(_bios)} from backdeck machine.")
                _success = True

            except Exception as e:
                _msg = f"Error while inserting backdeck bio data: {e}"
                self._logger.error(_msg)
        finally:
            self._logger.debug(f"Backdeck pull results: status: {_success}, {_msg} rows: {len(_bios)}")
            self.backdeckResults.emit(_success, _msg, len(_bios))
            self.pullComplete.emit()


class DataSelector(QObject):
    unusedSignal = Signal()
    haulIndexReset = Signal(int, arguments=['i'])
    curHaulChanged = Signal(str, arguments=['new_haul_num'])
    curCatchChanged = Signal(str, arguments=['new_catch'])
    curProjectChanged = Signal(str, arguments=['new_project'])
    curBioChanged = Signal(str, arguments=['new_bio'])
    newBackdeckData = Signal(int, arguments=['new_rows'])

    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._db = db
        self._logger = Logger.get_root()

        self._get_bios_thread = None

        # on init, get values that we've persisted to the db in state table
        self._cur_haul_num = self._app.state.get_state_value('Current Haul Number')
        self._cur_haul_id = self._app.state.get_state_value('Current Haul ID')
        self._cur_catch_display = self._app.state.get_state_value('Current Catch Display')
        self._cur_catch_id = self._app.state.get_state_value('Current Catch ID')
        self._cur_project_name = self._app.state.get_state_value('Current Project Name')
        self._cur_bio_label = self._app.state.get_state_value('Current Bio Label')
        self._cur_bio_id = self._app.state.get_state_value('Current Bio ID')

        # setup base models used for combobox listviews
        self._hauls_model = HaulsModel(db)
        self._hauls_model.loadModel()  # always load hauls model to start
        self._catches_model = CatchesModel(db)
        self._projects_model = ProjectsModel(db)
        self._bios_model = BiosModel(db)

        # proxy models will allow us to filter further based on upstream selections
        self._catches_proxy = FramCamFilterProxyModel(self._catches_model, name='CatchesProxy')
        self._projects_proxy = FramCamFilterProxyModel(self._projects_model, name='ProjectsProxy')
        self._bios_proxy = FramCamFilterProxyModel(self._bios_model, name='BiosProxy')

        # when one model changes, we need to do things to others  TODO: push this connection trigger down to cur property changed?
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
        if self._cur_haul_num:
            _haul_model_ix = self._hauls_model.getRowIndexByValue('haul_number', self._cur_haul_num)
            #_haul_id = self._hauls_model.getData(_haul_model_ix, 'fram_cam_haul_id')
            self._logger.debug(f"Setting initial HaulsModel row to {_haul_model_ix}, haul={self._cur_haul_num}")
            self._hauls_model.setIndexSilently(_haul_model_ix)
            self._on_haul_changed(_haul_model_ix)

        if self._cur_catch_display:
            _catch_model_ix = self._catches_model.getRowIndexByValue('display_name', self._cur_catch_display)
            self._logger.debug(f"Setting initial CatchesModel row to {_catch_model_ix},  catch display = {self._cur_catch_display}")
            self._catches_model.setIndexSilently(_catch_model_ix)
            self._on_catch_changed(_catch_model_ix)

        if self._cur_project_name and self._cur_catch_display:
            _projects_model_ix = self._projects_model.getItemIndex({'project_name': self._cur_project_name, 'display_name': self._cur_catch_display})
            _proxy_ix = self._projects_proxy.getProxyRowFromSource(_projects_model_ix)
            self._logger.debug(f"Setting initial ProjectsModel row to {_projects_model_ix}, proxy {_proxy_ix}, project {self._cur_project_name}")
            self._projects_model.setIndexSilently(_projects_model_ix)
            self._on_project_changed(_projects_model_ix)

        if self._app.state.cur_bio_label:
            _bios_model_ix = self._bios_model.getRowIndexByValue('bio_label', self._cur_bio_label)
            _proxy_ix = self._bios_proxy.getProxyRowFromSource(_bios_model_ix)
            self._logger.debug(f"Setting initial BiosModel row to {_bios_model_ix}, proxy {_proxy_ix} bio_label {self._cur_bio_label}")
            self._bios_model.setIndexSilently(_bios_model_ix)
            self._on_bio_changed(_bios_model_ix)

    def _refresh_after_backdeck_pull(self, status, msg, rows_retrieved):
        if status and rows_retrieved:
            # first, preserve values before doing anything to comboboxes
            _orig_haul_num = self._cur_haul_num
            _orig_catch_display = self._cur_catch_display
            _orig_project = self._cur_project_name
            _orig_bio = self._cur_bio_label
            _orig_filter_str = f'"display_name":"{_orig_catch_display or "NULL"}","project_name":"{_orig_project or "NULL"}"'

            # first, load hauls model, get new index based on haul num, then select
            self._hauls_model.loadModel()
            _haul_ix = self._hauls_model.getRowIndexByValue('haul_number', _orig_haul_num)
            self._hauls_model.selectIndexInUI.emit(_haul_ix)

            # catch model will update when haul is selected, then we get new index and select
            _catch_ix = self._catches_model.getRowIndexByValue('display_name', _orig_catch_display)
            _catch_proxy_ix = self._catches_proxy.getProxyRowFromSource(_catch_ix)
            self._catches_proxy.selectProxyIndexInUI.emit(_catch_proxy_ix)

            # projects reload as catch changes, find new index and select
            _project_ix = self._projects_model.getRowIndexByValue('bio_filter_str', _orig_filter_str)
            _project_proxy_ix = self._projects_proxy.getProxyRowFromSource(_project_ix)
            self._projects_proxy.selectProxyIndexInUI.emit(_project_proxy_ix)

            # bios reload as projects change, find new index and select
            _bio_ix = self._bios_model.getRowIndexByValue('bio_label', _orig_bio)
            _bio_proxy_ix = self._bios_proxy.getProxyRowFromSource(_bio_ix)
            self._bios_proxy.selectProxyIndexInUI.emit(_bio_proxy_ix)

            self.newBackdeckData.emit(rows_retrieved)


    @Slot()
    def getBackdeckBios(self):
        if isinstance(self._get_bios_thread, QThread) and self._get_bios_thread.isRunning():
            self._logger.info("Backdeck bios thread is busy, try again later")
            return

        # vars we need for data retrieval from backdeck
        self._get_bios_thread = QThread()
        self._get_bios_worker = GetBackdeckBiosWorker(app=self._app, db=self._db)
        self._get_bios_worker.cur_haul_num = self._cur_haul_num  # use haul num in request
        self._get_bios_worker.backdeckResults.connect(lambda status, msg, rows: self._refresh_after_backdeck_pull(status, msg, rows))
        self._get_bios_worker.moveToThread(self._get_bios_thread)
        self._get_bios_thread.started.connect(self._get_bios_worker.run)
        self._get_bios_worker.pullComplete.connect(self._get_bios_thread.quit)
        self._get_bios_thread.start()

    def _on_haul_changed(self, new_haul_index):
        # self.cur_haul_id =
        self.cur_haul_num = self._hauls_model.getData(new_haul_index, 'haul_number')
        _haul_num_binding = {':haul_number': self.cur_haul_num}
        self._catches_model.loadModel(bind_params=_haul_num_binding)
        self._projects_model.loadModel(bind_params=_haul_num_binding)
        self._bios_model.loadModel(bind_params=_haul_num_binding)

        # filter here should blank out these proxies (we want user to select a catch first)
        self._projects_proxy.filterRoleOnRegex('display_name', f'"display_name":"{self._cur_catch_display}"')
        self._bios_proxy.filterRoleOnRegex('bio_filter_str', f'"display_name":"{self._cur_catch_display}"')

    def _on_catch_changed(self, new_catch_index):
        """
        things to do when user changes the drop down for catch options.
        :param new_catch_index: new model index
        :return:
        """
        self.cur_catch_display = self._catches_model.getData(new_catch_index, 'display_name')
        #self.cur_catch_id = self._catches_model.getData(new_catch_index, 'fram_cam_catch_id')
        self._logger.info(f"Selected catch changed to {self._cur_catch_display}")
        self._projects_proxy.filterRoleWildcard('bio_filter_str', f'*"display_name":"{self._cur_catch_display}"*')
        self._bios_proxy.filterRoleWildcard('bio_filter_str', f'*"display_name":"{self._cur_catch_display}"*')

    def _on_project_changed(self, new_project_index):
        self.cur_project_name = self._projects_model.getData(new_project_index, 'project_name')
        self._logger.info(f"Selected project changed to {self._cur_project_name}")
        _wildcard = f'*"display_name":"{str(self._cur_catch_display) or "NULL"}","project_name":"{str(self._cur_project_name) or "NULL"}"*'
        self._logger.debug(f"Filtering bios menu: {_wildcard}")
        self._bios_proxy.filterRoleWildcard('bio_filter_str', _wildcard)

    def _on_bio_changed(self, new_bio_index):
        self.cur_bio_label = self._bios_model.getData(new_bio_index, 'bio_label')
        #self.cur_bio_id = self._bios_model.getData(new_bio_index, 'fram_cam_bio_id')
        self._logger.info(f"Selected bio label changed to {self._cur_bio_label}")

        # TODO: all of the next lines work, but tthings are pretty messy...
        if self._projects_model.currentIndex == -1 and new_bio_index > -1:
            self._logger.info("Bio label selected before project, trying to select project menu...")
            _proj = self._bios_model.getData(new_bio_index, 'project_name')
            _proj_ix = self._projects_model.getRowIndexByValue('bio_filter_str', f'"display_name":"{self._cur_catch_display}","project_name":"{_proj}"')
            _proxy_proj_ix = self._projects_proxy.getProxyRowFromSource(_proj_ix)
            self._projects_model.setIndexSilently(_proj_ix)
            self._on_project_changed(_proj_ix)


    @Property(QObject, notify=unusedSignal)
    def hauls_model(self):
        return self._hauls_model

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

    def set_combo_box_haul(self, haul_num):
        _haul_model_ix = self._hauls_model.getRowIndexByValue('haul_number', haul_num)
        self._hauls_model.selectIndexInUI.emit(_haul_model_ix)

    def set_combo_box_catch(self, display_name):
        _catch_model_ix = self._catches_model.getRowIndexByValue('display_name', display_name)
        self._catches_model.selectIndexInUI.emit(_catch_model_ix)

    def set_combo_box_proj(self, proj, display):
        _projects_model_ix = self._projects_model.getItemIndex({'project_name': proj, 'display_name': display})
        _proxy_ix = self._projects_proxy.getProxyRowFromSource(_projects_model_ix)
        self._projects_proxy.selectProxyIndexInUI.emit(_proxy_ix)

    def set_combo_box_bio(self, bio):
        _bios_model_ix = self._bios_model.getRowIndexByValue('bio_label', bio)
        _proxy_ix = self._bios_proxy.getProxyRowFromSource(_bios_model_ix)
        self._bios_proxy.selectProxyIndexInUI.emit(_proxy_ix)

    @Property(str, notify=curHaulChanged)
    def cur_haul_num(self):
        return self._cur_haul_num

    @cur_haul_num.setter
    def cur_haul_num(self, new_haul_num):
        if self._cur_haul_num != new_haul_num:
            self._cur_haul_num = new_haul_num
            self._app.state.set_state_value('Current Haul Number', new_haul_num)
            self.curHaulChanged.emit(new_haul_num)

    @Property(str, notify=curHaulChanged)
    def cur_haul_id(self):
        return self._cur_haul_id

    @cur_haul_id.setter
    def cur_haul_id(self, new_haul_id):
        if self._cur_haul_id != new_haul_id:
            self._cur_haul_id = new_haul_id
            self._app.state.set_state_value('Current Haul ID', new_haul_id)

    @Property(str, notify=curCatchChanged)
    def cur_catch_display(self):
        return self._cur_catch_display

    @cur_catch_display.setter
    def cur_catch_display(self, new_catch_display):
        self._logger.debug(f"Setting catch display to {new_catch_display}")
        if self._cur_catch_display != new_catch_display:
            self._cur_catch_display = new_catch_display
            self._app.state.set_state_value('Current Catch Display', new_catch_display)
            self.curCatchChanged.emit(new_catch_display)

    @Property(str, notify=curCatchChanged)
    def cur_catch_id(self):
        return self._cur_catch_id

    @cur_catch_id.setter
    def cur_catch_id(self, new_catch_id):
        self._logger.error(f"Setting catch id to {new_catch_id}")
        if self._cur_catch_id != new_catch_id:
            self._cur_catch_id = new_catch_id
            self._app.state.set_state_value('Current Catch ID', new_catch_id)

    @Property(str, notify=curProjectChanged)
    def cur_project_name(self):
        return self._cur_project_name

    @cur_project_name.setter
    def cur_project_name(self, new_project_name):
        self._logger.error(f"Setting project to {new_project_name}")
        if self._cur_project_name != new_project_name:
            self._cur_project_name = new_project_name
            self._app.state.set_state_value('Current Project Name', new_project_name)
            self.curProjectChanged.emit(new_project_name)

    @Property(str, notify=curBioChanged)
    def cur_bio_label(self):
        return self._cur_bio_label

    @cur_bio_label.setter
    def cur_bio_label(self, new_bio_label):
        if self._cur_bio_label != new_bio_label:
            self._cur_bio_label = new_bio_label
            self._app.state.set_state_value('Current Bio Label', new_bio_label)
            self.curBioChanged.emit(new_bio_label)

    @Property(str, notify=unusedSignal)
    def cur_bio_id(self):
        return self._cur_bio_id

    @cur_bio_id.setter
    def cur_bio_id(self, new_bio_id):
        if self._cur_bio_id != new_bio_id:
            self._cur_bio_id = new_bio_id
            self._app.state.set_state_value('Current Bio ID', new_bio_id)
