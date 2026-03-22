update 
	raw_data
set
	price_total = round(price_total, -6),
	area = round(area, 2),
	price_per_m2 = round(round(price_total, -6) / round(area, 2), 2),
	frontage = round(frontage, 2),
	road_width = round(road_width, 2)