import sklearn.neighbors
import sqlite3

def station_code_to_number(code):
	a, b, c = code
	return (ord(a) - ord("A")) * 26 * 26 + (ord(b) - ord("A")) * 26 + (ord(c) - ord("A"))

def time_string_to_hour_minute(time):
	return int(time[:2]), int(time[2:])

db = sqlite3.connect("data/hsp.db")
cur = db.cursor()
result = cur.execute("SELECT services.id, services.origin_location, services.destination_location, services.gbtt_ptd, services.gbtt_pta, services.toc_code, services.date_of_service, services.rid, locations.location, locations.gbtt_ptd, locations.gbtt_pta, locations.actual_td, locations.actual_ta, locations.late_canc_reason FROM services INNER JOIN locations ON services.id = locations.service_id")
rows = [row for row in result]

def predict_it(row1, from_station, to_station):	
	knnc = sklearn.neighbors.KNeighborsClassifier()

	train_data = []
	target_data = []
	
	total_delay = 0
	cur_service_id = None
	for services_id, services_origin_location, services_destination_location, services_gbtt_ptd, services_gbtt_pta, services_toc_code, services_date_of_service, services_rid, locations_location, locations_gbtt_ptd, locations_gbtt_pta, locations_actual_td, locations_actual_ta, locations_late_canc_reason in rows:
		# if services_origin_location != from_station.get_code() or services_destination_location != to_station.get_code():
		# 	continue
		
		if cur_service_id != services_id:
			for i in range(len(train_data) - len(target_data)):
				target_data.append(total_delay)
			total_delay = 0
			cur_service_id = services_id
		
		if locations_gbtt_pta != "" and locations_actual_ta != "" and locations_late_canc_reason == "":
			predicted_hour, predicted_minute = time_string_to_hour_minute(locations_gbtt_pta)
			actual_hour, actual_minute = time_string_to_hour_minute(locations_actual_ta)
			predicted = predicted_hour * 60 + predicted_minute
			actual = actual_hour * 60 + actual_minute
			delay = actual - predicted if abs(actual - predicted) < abs(actual + 1440 - predicted) else actual + 1440 - predicted
			
			if delay > 0:
				total_delay += delay

				train_data.append([
					*map(int, services_date_of_service.split("-")),
					station_code_to_number(services_origin_location),
					station_code_to_number(services_destination_location),
					station_code_to_number(locations_location),
					*time_string_to_hour_minute(locations_gbtt_pta),
					*time_string_to_hour_minute(locations_actual_ta)
				])

	for i in range(len(train_data) - len(target_data)):
		target_data.append(total_delay)

	knnc.fit(train_data, target_data)
	
	try:
		return knnc.predict([row1])
	except:
		return 0
	
