import requests
import pprint
import datetime
from ticket_generator import Station
import sklearn.neighbors
import sqlite3
import time
import random

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
	N = 0
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
		N += 1

		if response.status_code != 200:
			continue

		metrics = response.json()
		print(metrics)

		if "Services" not in metrics:
			continue
		for metric in metrics["Services"]:
			print(metric)
			rids = metric["serviceAttributesMetrics"]["rids"]
			for rid in rids:
				response = requests.post("https://hsp-prod.rockshore.net/api/v1/serviceDetails", auth = (EMAIL, PASSWORD), json = {
					"rid": rid
				})
				N += 1
				details = response.json()
				print(details)

				try:
					cur.execute("INSERT INTO services VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", [metric["serviceAttributesMetrics"]["origin_location"], metric["serviceAttributesMetrics"]["destination_location"], metric["serviceAttributesMetrics"]["gbtt_ptd"], metric["serviceAttributesMetrics"]["gbtt_pta"], metric["serviceAttributesMetrics"]["toc_code"], details["serviceAttributesDetails"]["date_of_service"], details["serviceAttributesDetails"]["rid"]])
				except:
					continue

				s_id = cur.lastrowid

				for location in details["serviceAttributesDetails"]["locations"]:
					cur.execute("INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?, ?)", [s_id, location["location"], location["gbtt_ptd"], location["gbtt_pta"], location["actual_td"], location["actual_ta"], location["late_canc_reason"]])
					print(location)
			
				db.commit()
	return N

def download_data_both(from_station, to_station, from_date, to_date):
	return download_data(from_station, to_station, from_date, to_date) + download_data(to_station, from_station, from_date, to_date)
		
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

# for i in range(1, 13):
# 	download_data(Station.get_from_code("NRW"), Station.get_from_code("SSD"), datetime.datetime(year = 2020, month = i, day = 1), datetime.datetime(year = 2020, month = i, day = 1) + datetime.timedelta(days = 32))
# 	time.sleep(2 * 60)

# cities = ["Cambridge", "London", "Peterborough", "Ipswich", "Heathrow", "Aberystwyth", "Bournemouth", "Portsmouth", "Southampton", "Brighton", "Stevenage", "Dover", "Reading", "Oxford", "Swindon", "Bath", "Swansea", "Cardiff", "Bristol", "Exeter", "Plymouth", "Penzance", "Leicester", "Coventry", "Watford", "Gatwick", "Ashford", "Derby", "Nottingham", "Birmingham", "Wolverhampton", "Bangor", "Stoke", "Manchester", "Blackpool", "Preston", "Bradford", "Leeds", "Doncaster", "Grimsby", "Hull", "York", "Scarborough", "Grimsby", "Newcastle", "Carlisle", "Prestwick", "Edinburgh", "Stirling", "Perth", "Aberdeen", "Inverness", "Glasgow", "Norwich"]
# city_stations = [station for station in Station.get_stations() if any(city in station.get_name() for city in cities)]

# print(city_stations[90:])
# exit()

# for i in range(20):
# 	print(i)
# 	# first = random.choice(city_stations)
# 	first = Station.get_from_name("Norwich")
# 	second = first
# 	while second == first:
# 		second = random.choice(city_stations)	
# 	print(first, "->", second)
# 	N = download_data(first, second, datetime.datetime.now() - datetime.timedelta(weeks = 52), datetime.datetime.now())
# 	N += download_data(second, first, datetime.datetime.now() - datetime.timedelta(weeks = 52), datetime.datetime.now())
# 	print(N, "requests")

# 	if N > 20:
# 		time.sleep(60 * 5)
# 	else:
# 		time.sleep(10)

# [download_data_both(Station.get_from_name("Norwich"), Station.get_from_name(name), datetime.datetime.now() - datetime.timedelta(weeks = 52), datetime.datetime.now()) for name in [
# 	"Peterborough",
# 	"Ely",
# 	"Stansted",
# 	"Manchester",
# 	"Birmingham",
# 	"Edinburgh"
# ]]


# for city_station in city_stations[15:]:
# 	if city_station != Station.get_from_name("Norwich"):
# 		download_data_both(Station.get_from_name("Norwich"), city_station, datetime.datetime.now() - datetime.timedelta(weeks = 52), datetime.datetime.now())

download_data_both(Station.get_from_name(input("From: ")), Station.get_from_name(input("To: ")), datetime.datetime.now() - datetime.timedelta(weeks = 52 // 2), datetime.datetime.now()- datetime.timedelta(weeks = 0))

