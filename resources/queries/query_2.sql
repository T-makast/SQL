select
	weeks."date"::date as "week",
	coalesce(sum(oc.quantity), 0) as "n_items",
	coalesce(sum(oc.quantity), 0) - lag(coalesce(sum(oc.quantity), 0)) over (order by weeks."date"::date) as delta
from orders o
	join order_contents oc on o.id = oc.order_id
	join goods g on g.id = oc.good_id
	join wood_types wt on wt.id = g.wood_type_id
	right join (
		select 
			generate_series(
			date_trunc('week', '2017-06-01'::date),
			'2017-08-31'::date,
			'1 week'::interval)
	) as weeks("date") on weeks."date" = date_trunc('week', o.ordered_ts)
group by weeks."date"
order by weeks."date"