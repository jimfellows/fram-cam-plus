-- IMAGES_VW source

drop view images_vw
CREATE VIEW IMAGES_VW as 
select
			
			h."HAUL_NUMBER"
			,c.display_name
			,b.project_name
			,b.project_scientist
			,b.bio_label
			,b.bio_type
			,b.bio_subtype
			,i.IMAGE_ID
			,i.FILE_PATH
			,i.FILE_NAME
			,i.FILE_PATH || '/' || i.FILE_NAME as FULL_PATH
			,i.FRAM_CAM_HAUL_ID
			,i.FRAM_CAM_CATCH_ID
			,i.FRAM_CAM_BIO_ID
			,i.IS_BACKED_UP
			,i.NOTES
			,i.CAPTURED_DT
			,'"haul_number":"'||h.haul_number||'","display_name":"'||c.display_name||'","project_name":"'||b.project_name||'","bio_label":"'||b.bio_label||'"' as image_filter_str

from 		images i
left join	fram_cam_hauls h
			on i.fram_cam_haul_id = h.fram_cam_HAUL_ID
left JOIN 	fram_cam_catch c
			on c.fram_cam_catch_id = i.fram_cam_catch_id
left JOIN 	fram_cam_bios b
			on b.FRAM_CAM_BIO_ID = i.fram_cam_bio_id
order by 	datetime(i.CAPTURED_DT) desc
;