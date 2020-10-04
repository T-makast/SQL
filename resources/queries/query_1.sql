with set_wood as(
	select
		aux.length_m as "length",
		aux.diameter_cm as "diameter",
		sum(aux.quantity) as "n_items"
	from (
		select
			g.length_m,
			g.diameter_cm,
			oc.quantity,
			o.ordered_ts
		from orders o
			join order_contents oc on oc.order_id = o.id
			join goods g on g.id = oc.good_id
		where extract('year' from o.ordered_ts) = 2018
	) as aux
	group by "length", "diameter"
	order by "length", "n_items"
),
aux_2 as (
	select
		sw.length,
		sw.diameter,
		sw.n_items,
		row_number() over(partition by sw.length order by sw.n_items desc) as rk
	from set_wood sw
	)
select
	concat(a.length::int, ' m ', a.diameter, ' cm') as "type",
	a.n_items
from aux_2 a
where a.rk = 1
order by length, diameter