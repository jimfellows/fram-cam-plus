-- IMAGES definition
drop table if exists images;
CREATE TABLE IMAGES (
	IMAGE_ID integer not null primary key autoincrement
	,BACKDECK_BIOS_LOG_ID int
	,FILE_PATH text
	,FILE_NAME text
	,BACKUP_PATH text
	,IS_BACKED_UP integer default 0
	,NOTES text
	,CAPTURED_DT text
	,HAUL_NUMBER text
	,CATCH_DISPLAY_NAME text
	,COMMON_NAME text
	,SCIENTIFIC_NAME text
	,BIO_LABEL text
	,BIO_TYPE text
	,BIO_SUBTYPE text
	,PROJECT_NAME text
	,PROJECT_SCIENTIST text
	,TAXONOMY_ID integer
	,BACKDECK_HAUL_ID integer
	,BACKDECK_CATCH_ID integer
	,BACKDECK_SPECIMEN_ID integer
	,BACKDECK_SPECIMEN_ATTR_ID integer
);

