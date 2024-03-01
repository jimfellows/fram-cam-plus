-- IMAGES_VW source

CREATE VIEW IMAGES_VW as 
select
			
			h."HAUL_NUMBER"
			,c.display_name as "CATCH_DISPLAY_NAME"
			,sp.plan_name as "PROJECT_NAME"
			,coalesce(s.alpha_value, cast(cast(s.numeric_value as int) as text)) as BIO_LABEL
			,i.IMAGE_ID
			,i.FILE_PATH
			,i.FILE_NAME
			,i.FILE_PATH || '/' || i.FILE_NAME as FULL_PATH
			,i.HAUL_ID
			,i.CATCH_ID
			,i.SPECIMEN_ID
			,s.SPECIES_SAMPLING_PLAN_ID
			,i.IS_BACKED_UP
			,i.NOTES
			,i.CAPTURED_DT

from 		images i
left join	hauls h
			on i.haul_id = h.HAUL_ID
left JOIN 	catch c
			on c.catch_id = i.catch_id
left JOIN 	specimen s
			on s.specimen_id = i.specimen_id
left JOIN 	SPECIES_SAMPLING_PLAN_LU sp
			on s.SPECIES_SAMPLING_PLAN_ID = sp.species_sampling_plan_id
order by 	datetime(i.CAPTURED_DT) desc;