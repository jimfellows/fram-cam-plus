-- FRAM_CAM_STATE definition

CREATE TABLE "FRAM_CAM_STATE" (
	FRAM_CAM_SETTINGS_ID integer primary key autoincrement
	,PARAMETER text
	,VALUE text
	,LAST_MODIFIED_DT text
, is_user_settin