import sklearn.neighbors
import sqlite3

def station_code_to_number(code):
	a, b, c = code
	return (ord(a) - ord("A")) * 26 * 26 + (ord(b) - ord("A")) * 26 + (ord(c) - ord("A"))

def time_string_to_hour_minute(time):
	return int(time[:2]), int(time[2:])

db = sqlite3.connect("data/hsp.db")
cur = db.cursor()

knn = sklearn.neighbors.KNeighborsClassifier()

train_data = []
target_data = []

result = cur.execute("SELECT services.id, services.origin_location, services.destination_location, services.gbtt_ptd, services.gbtt_pta, services.toc_code, services.date_of_service, services.rid, locations.location, locations.gbtt_ptd, locations.gbtt_pta, locations.actual_td, locations.actual_ta, locations.late_canc_reason FROM services INNER JOIN locations on services.id = locations.service_id")
for services_id, services_origin_location, services_destination_location, services_gbtt_ptd, services_gbtt_pta, services_toc_code, services_date_of_service, services_rid, locations_location, locations_gbtt_ptd, locations_gbtt_pta, locations_actual_td, locations_actual_ta, locations_late_canc_reason in result:
	if locations_gbtt_pta != "" and locations_actual_ta != "" and locations_late_canc_reason == "":
		predicted_hour, predicted_minute = time_string_to_hour_minute(locations_gbtt_pta)
		actual_hour, actual_minute = time_string_to_hour_minute(locations_actual_ta)
		predicted = predicted_hour * 60 + predicted_minute
		actual = actual_hour * 60 + actual_minute
		delay = actual - predicted if abs(actual - predicted) < abs(actual + 1440 - predicted) else actual + 1440 - predicted

		if delay > 3:
			train_data.append([
				*map(int, services_date_of_service.split("-")),
				# int(services_rid),
				station_code_to_number(locations_location),
				*time_string_to_hour_minute(locations_gbtt_pta),
				*time_string_to_hour_minute(locations_actual_ta),
				station_code_to_number(services_destination_location)
			])
			# print(train_data[-1], delay)

			target_data.append(delay)

knn.fit(train_data, target_data)
	
cur.close()
db.close()
