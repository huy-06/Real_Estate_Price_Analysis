delete from
	raw_data
where category in (
	select 
		category
	from
		raw_data
	group by
		category
	having
		count(*) < 1000
)