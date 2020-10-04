select
    aux.month,
	aux.client_type,
	sum(rev) as "revenue"
from(
	select 
		coalesce(c.client_type, 'розница') as "client_type",
		to_char(date_trunc('month', o.ordered_ts), 'YYYY-MM') as "month",
			g.length_m, (oc.quantity * p.price) as "rev"
	from orders o 
	join order_contents oc
		on o.id=oc.order_id
		left join clients c on c.id=o.client_id
		join goods g on oc.good_id=g.id
		join wood_types wt on wt.id=g.wood_type_id
		join prices p on p.good_id = g.id and extract('year' from o.ordered_ts)=extract('year' from p.date_start)
	where for_ships or for_houses
	) as aux
where length_m > 10
group by aux.month, aux.client_type
order by aux.month, revenue desc