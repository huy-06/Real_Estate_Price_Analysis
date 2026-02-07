delete from 
	raw_data
where post_id in (
	select 
		post_id
	from (
		select
			post_id,
			price_total,
			avg(price_total) over (partition by category) as avg_price,
			stdev(price_total) over (partition by category) as std_dev
		from
			raw_data
	) as calc_table
where
	price_total > (avg_price + 3 * std_dev)
)