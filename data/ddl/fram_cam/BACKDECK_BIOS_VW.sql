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
			,'"display_name":"'||coalesce(display_name, 'NULL') || '","project_name":"'||coalesce(project_name, 'NULL') ||'"' as BIO_FILTER_STR

from 		backdeck_bios_log t
)
where	batch_rank = 1
;

select * from 

create table backdeck_bios_Log_bu as select * from backdeck_bios_log;

select * from backdeck_bios_Log_bu;
insert into backdeck_bios_log select * from backdeck_bios_log_bu;


drop table backdeck_bios_log;
drop table backdeck_hauls_log;


