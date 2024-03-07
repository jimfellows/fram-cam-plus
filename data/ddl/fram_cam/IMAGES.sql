-- IMAGES definition

CREATE TABLE IMAGES (
	IMAGE_ID integer not null primary key autoincrement
	,BACKDECK_CLIENT_ID int
	,FILE_PATH text
	,FILE_NAME text
	,HAUL_ID int
	,CATCH_ID int
	,SPECIMEN_ID int
	,SPECIES_SAMPLING_PLAN_ID int
	,IS_BACKED_UP int default 0
	,NOTES text
	,CAPTURED_DT text	
);