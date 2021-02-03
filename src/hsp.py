import requests
import pprint
import datetime
from ticket_generator import Station
import sklearn.neighbors
import sqlite3
import time

EMAIL = ""
PASSWORD = ""

try:
	with open("src/passwords.txt") as f:
		EMAIL, PASSWORD = f.read().split(",")
except:
	pass

def station_code_to_number(code):
	a, b, c = code
	return (ord(a) - ord("A")) * 26 * 26 + (ord(b) - ord("A")) * 26 + (ord(c) - ord("A"))

def time_to_number(hour, minute):
	return hour * 60 + minute

db = sqlite3.connect("data/hsp.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, origin_location TEXT, destination_location TEXT, gbtt_ptd TEXT, gbtt_pta TEXT, toc_code TEXT, date_of_service TEXT, rid INTEGER UNIQUE)")
cur.execute("CREATE TABLE IF NOT EXISTS locations (service_id INTEGER, location TEXT, gbtt_ptd TEXT, gbtt_pta TEXT, actual_td TEXT, actual_ta TEXT, late_canc_reason TEXT, FOREIGN KEY (service_id) REFERENCES services(id))")
db.commit()

def download_data(from_station, to_station, from_date, to_date):
	for day_type in ["WEEKDAY", "SATURDAY", "SUNDAY"]:
		response = requests.post("https://hsp-prod.rockshore.net/api/v1/serviceMetrics", auth = (EMAIL, PASSWORD), json = {
			"from_loc": from_station.get_code(),
			"to_loc": to_station.get_code(),
			"from_time": "0000",
			"to_time": "2359",
			"from_date": from_date.strftime("%Y-%m-%d"),
			"to_date": to_date.strftime("%Y-%m-%d"),
			"days": day_type
		})
		metrics = response.json()
		for metric in metrics["Services"]:
			# print(metric)
			rids = metric["serviceAttributesMetrics"]["rids"]
			for rid in rids:
				response = requests.post("https://hsp-prod.rockshore.net/api/v1/serviceDetails", auth = (EMAIL, PASSWORD), json = {
					"rid": rid
				})
				details = response.json()
				print(details)

				try:
					cur.execute("INSERT INTO services VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", [metric["serviceAttributesMetrics"]["origin_location"], metric["serviceAttributesMetrics"]["destination_location"], metric["serviceAttributesMetrics"]["gbtt_ptd"], metric["serviceAttributesMetrics"]["gbtt_pta"], metric["serviceAttributesMetrics"]["toc_code"], details["serviceAttributesDetails"]["date_of_service"], details["serviceAttributesDetails"]["rid"]])
				except:
					continue

				for location in details["serviceAttributesDetails"]["locations"]:
					cur.execute("INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?, ?)", [cur.lastrowid, location["location"], location["gbtt_ptd"], location["gbtt_pta"], location["actual_td"], location["actual_ta"], location["late_canc_reason"]])
					print(location)
			
		db.commit()
		

def train_data(from_station, to_station, from_date, to_date):
	for day_type in ["WEEKDAY", "SATURDAY", "SUNDAY"]:
		response = requests.post("https://hsp-prod.rockshore.net/api/v1/serviceMetrics", auth = (EMAIL, PASSWORD), json = {
			"from_loc": from_station.get_code(),
			"to_loc": to_station.get_code(),
			"from_time": "0000",
			"to_time": "2359",
			"from_date": from_date.strftime("%Y-%m-%d"),
			"to_date": to_date.strftime("%Y-%m-%d"),
			"days": day_type
		})

		x = response.json()
		for o in x["Services"]:
			# print(o["serviceAttributesMetrics"])
			rids = o["serviceAttributesMetrics"]["rids"]
			for rid in rids:
				response = requests.post("https://hsp-prod.rockshore.net/api/v1/serviceDetails", auth = (EMAIL, PASSWORD), json = {
					"rid": rid
				})

				q = response.json()["serviceAttributesDetails"]
				# print(q["date_of_service"])
				dos = q["date_of_service"].split("-")
				# print(q["rid"])
				for loc in q["locations"]:
					location, gbtt_pta, gbtt_ptd, actual_ta, actual_td = loc["location"], loc["gbtt_pta"], loc["gbtt_ptd"], loc["actual_ta"], loc["actual_td"]

					if gbtt_pta != "" and gbtt_ptd != "" and actual_ta != "" and actual_td != "":

						gbtt_pta_h = int(gbtt_pta[:2])
						gbtt_pta_m = int(gbtt_pta[2:])
						gbtt_pta_n = time_to_number(gbtt_pta_h, gbtt_pta_m)
						
						gbtt_ptd_h = int(gbtt_ptd[:2])
						gbtt_ptd_m = int(gbtt_ptd[2:])
						gbtt_ptd_n = time_to_number(gbtt_ptd_h, gbtt_ptd_m)

						actual_ta_h = int(actual_ta[:2])
						actual_ta_m = int(actual_ta[2:])
						actual_ta_n = time_to_number(actual_ta_h, actual_ta_m)

						actual_td_h = int(actual_td[:2])
						actual_td_m = int(actual_td[2:])
						actual_td_n = time_to_number(actual_td_h, actual_td_m)

						def diff(n, m):
							return m - n if abs(m - n) < abs((m + 24 * 60) - n) else (m + 24 * 60) - n

						if diff(gbtt_ptd_n, actual_td_n) == -33:
							print(gbtt_ptd, gbtt_ptd_h, gbtt_ptd_m, gbtt_ptd_n)
							print(actual_td, actual_td_h, actual_td_m, actual_td_n)
							
							exit()

						yield [[int(dos[0]), int(dos[1]), int(dos[2]), gbtt_pta_h, gbtt_pta_m, gbtt_ptd_h, gbtt_ptd_m, actual_ta_h, actual_ta_m, actual_td_h, actual_td_m], diff(gbtt_ptd_n, actual_td_n)]

# knn = sklearn.neighbors.KNeighborsClassifier()
# X = []
# y = []
# for t in train_data(Station.get_from_code("NRW"), Station.get_from_code("SSD"), datetime.datetime(year = 2020, month = 10, day = 1), datetime.datetime.now()):
# 	if True or (t[1] > 5):
# 		print(t)
# 		X.append(t[0])
# 		y.append(t[1])

# knn.fit(X, y)
# # [[2020, 10, 16, 10, 6, 10, 7, 10, 10, 10, 11], 4]
# print(knn.predict([[2020, 10, 16, 10, 6, 10, 7, 10, 10, 10, 11]]))

for i in range(1, 13):
	download_data(Station.get_from_code("NRW"), Station.get_from_code("SSD"), datetime.datetime(year = 2020, month = i, day = 1), datetime.datetime(year = 2020, month = i, day = 1) + datetime.timedelta(days = 32))
	time.sleep(2 * 60)