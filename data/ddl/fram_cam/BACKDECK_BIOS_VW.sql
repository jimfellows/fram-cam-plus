
drop view if exists backdeck_bios_vw;

CREATE VIEW BACKDECK_BIOS_VW as
select
			*
from 		(
select
			datetime(inserted_dt) as INSERT_DT
			,dense_rank() over (
				partition by haul_number
				order by datetime(inserted_dt) desc
			) as BATCH_RANK
			,t.*
			,'"catch_display_name":"'||coalesce(catch_display_name, 'NULL') || '","project_name":"'||coalesce(project_name, 'NULL') ||'"' as BIO_FILTER_STR

from 		backdeck_bios_log t
)
where	batch_rank = 1
;


