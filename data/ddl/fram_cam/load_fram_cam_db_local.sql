

select * from backdeck_clients;

--create client rec
insert into backdeck_clients (client_name) values ((select value from settings where parameter = 'Backdeck CPU ID'));

--load hauls
select * from fram_cam_hauls;
insert into fram_cam_hauls (backdeck_client_id, backdeck_haul_id, haul_number)

SELECT
	(
		select backdeck_client_id
		from backdeck_clients WHERE client_name = (select value from settings where parameter = 'Backdeck CPU ID')
	) as backdeck_client_id
	,haul_id
	,haul_number
FROM 
	hauls
;

--load catches
select * from fram_cam_catch;

insert into fram_cam_catch (fram_cam_haul_id, backdeck_catch_id, display_name, common_name, scientific_name)

SELECT 
			(select fram_cam_haul_id from fram_cam_hauls where haul_number = h.haul_number) as fram_cam_haul_id
			,c.catch_id
			,c.display_name
			,tl.COMMON_NAME_1
			,tl.SCIENTIFIC_NAME 
from 		catch c
join		CATCH_CONTENT_LU ccl 
			on c.CATCH_CONTENT_ID = ccl.CATCH_CONTENT_ID 
JOIN 		TAXONOMY_LU tl 	
			on ccl.TAXONOMY_ID = tl.TAXONOMY_ID 
join		hauls h
			on h.haul_id = c.operation_id
WHERE 		c.receptacle_seq is null
;

--load bios
select * from fram_cam_bios;
insert into fram_cam_bios (fram_cam_catch_id, backdeck_parent_specimen_id, backdeck_specimen_id, project_name, project_scientist, bio_label, bio_type, bio_subtype)
select
			(select fram_cam_catch_id from fram_cam_catch c1 join fram_cam_hauls h1 on c1.fram_cam_haul_id = h1.fram_cam_Haul_id 
			where c1.display_name = c.display_name and h.haul_number = h1.haul_number ) as FRAM_CAM_CATCH_ID
			,s.parent_specimen_id
			,s.specimen_id
			,sp.plan_name
			,case when pil.full_name = 'FRAM Standard Survey' then null else pil.full_name end as project_scientist
			,coalesce(s.alpha_value, cast(cast(numeric_value as int) as text)) as BIO_LABEL
			,t.type as BIO_TYPE
			,t.subtype as BIO_SUBTYPE
			
			
from 		specimen s
join		catch c
			on s.catch_id = c.CATCH_ID 
JOIN 		hauls h
			on c.operation_id = h.haul_id
JOIN 		SPECIES_SAMPLING_PLAN_LU SP
			on s.SPECIES_SAMPLING_PLAN_ID = sp.SPECIES_SAMPLING_PLAN_ID 
LEFT JOIN 	PRINCIPAL_INVESTIGATOR_LU pil 
			on sp.PRINCIPAL_INVESTIGATOR_ID = pil.PRINCIPAL_INVESTIGATOR_ID 
JOIN 		types_lu t
			on s.ACTION_TYPE_ID = t.type_id

WHERE 		s.PARENT_SPECIMEN_ID is not null
			and t.type like '% ID'
			and coalesce(s.alpha_value, cast(cast(numeric_value as int) as text)) != '0'
			
;
