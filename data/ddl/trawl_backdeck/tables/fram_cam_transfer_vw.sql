CREATE view		fram_cam_transfer_vw as
SELECT
			(select value from settings where parameter = 'Backdeck CPU ID') as BACKDECK_CLIENT_NAME
			,h."HAUL_NUMBER"
			,c.display_name as "CATCH_DISPLAY_NAME"
			,sp.plan_name as "PROJECT_NAME"
			,coalesce(s.alpha_value, cast(cast(s.numeric_value as int) as text)) as BIO_LABEL
			,coalesce(t.subtype, t.type) as BIO_TYPE
from		hauls h
left JOIN 	catch c
			on c.operation_id = h.haul_id
			and c.receptacle_seq is null
left JOIN 	specimen s
			on s.catch_id = c.catch_id
			and s.parent_specimen_id is not null
left JOIN 	SPECIES_SAMPLING_PLAN_LU sp
			on s.SPECIES_SAMPLING_PLAN_ID = sp.species_sampling_plan_id
left JOIN 	types_lu t
			on s.action_type_id = t.TYPE_ID 
WHERE 		t.type is null or t.type like '% ID'