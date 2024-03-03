
drop view if exists bio_options_vw;
create view BIO_OPTIONS_VW as
 SELECT
 			h.HAUL_NUMBER
 			,c.display_name
 			,b.project_name
 			,b.project_scientist
 			,b.bio_label
 			,b.bio_type
 			,b.bio_subtype
 			,row_number() over (
 				partition by haul_number, c.display_name, b.bio_label
 				order by h.backdeck_client_id DESC, h.fram_cam_haul_id desc
 			) as OPT_INSTANCE
 			,h.fram_cam_haul_id
 			,h.backdeck_haul_id
 			,c.fram_cam_catch_id
 			,c.backdeck_catch_id
 			,b.fram_cam_bio_id
 			,b.backdeck_parent_specimen_id
 			,b.backdeck_specimen_id
			,'","display_name":"'||coalesce(c.display_name, 'NULL') || '","project_name":"'||coalesce(b.project_name, 'NULL') as BIO_FILTER_STR
 			
 from 		fram_cam_hauls h
 LEFT JOIN	fram_cam_catch c
 			on h.fram_cam_haul_id = c.FRAM_CAM_HAUL_ID 
 			and c.is_deleted = 0
 left JOIN 	fram_cam_bios b
 			on c.fram_cam_catch_id = b.fram_cam_catch_id
 			and b.is_deleted = 0
 			
 	
 			
 			;
 			
 		
 		            select  distinct
                    project_name
                    ,project_scientist
                    ,display_name
            from    BIO_OPTIONS_VW
            where   opt_instance = 1
                    and c.fram_cam_haul_id = 1