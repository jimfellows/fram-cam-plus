drop view if exists images_vw;
CREATE VIEW IMAGES_VW as 

select 
			i.*
			,i.FILE_PATH || '/' || i.FILE_NAME as FULL_PATH
			,'"haul_number":"'||haul_number||'","catch_display_name":"'||catch_display_name||'","project_name":"'||project_name||'","bio_label":"'||bio_label||'"' as IMAGE_FILTER_STR						
from 		images i
			;
			
			
			