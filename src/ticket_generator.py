import requests
import bs4
import re
import json
import datetime
import urllib.parse

class Station:
	def __init__(self, name, postcode, code):
		self.name = name
		self.postcode = postcode
		self.code = code

	def get_name(self):
		return self.name

	def get_postcode(self):
		return self.postcode

	def get_code(self):
		return self.code

	def __str__(self):
		return f"Station<{self.name!r}, {self.postcode!r}, {self.code!r}>"

	def __repr__(self):
		return str(self)

	@staticmethod
	def get_stations():
		with open("data/stations.json", "r") as f:
			return [Station(row["name"], row["postcode"], row["code"]) for row in json.load(f)]

	@staticmethod
	def is_a_station(station_name):
		stations = Station.get_stations()
		for station in stations:
			if station_name == station.get_name() or station_name == station.get_code() or station_name == station.get_postcode():
				return True
		return False

	@staticmethod
	def get_from_name(name):
		for station in Station.get_stations():
			if station.get_name() == name:
				return station
		return None
	
	@staticmethod
	def get_from_code(code):
		for station in Station.get_stations():
			if station.get_code() == code:
				return station
		return None

class Ticket:
	def __init__(self, from_station, to_station, leave_at, arrive_at, no_changes, price, name, provider, link = None):
		self.from_station = from_station
		self.to_station = to_station
		self.leave_at = leave_at
		self.arrive_at = arrive_at
		self.travel_time = arrive_at - leave_at
		self.no_of_changes = no_changes
		self.price = price
		self.name = name
		self.provider = provider
		self.link = link
	
	def get_price(self):
		return self.price

	def __str__(self):
		return f"Ticket<{self.from_station}, {self.to_station}, {self.leave_at}, {self.arrive_at}, {self.travel_time}, {self.no_of_changes}, {self.price}, {self.name!r}, {self.provider!r}>"

	def __repr__(self):
		return str(self)

class Railcard:
	def __init__(self):
		pass

def get_tickets(from_station, to_station, when = None, arriving = False, is_return = False, return_when = None, return_arriving = False, adults = 1, children = 0, railcards = []):
	if not when:
		when = datetime.datetime.now()
	if not return_when:
		return_when = datetime.datetime.now()

	# You have to get these 3 pages before the main request or it doesn't work.
	# Do I know why? No. Not really. It's probably to do with cookies.
	# But that's someone else's problem now. :)
	session = requests.Session()
	session.get("https://www.nationalrail.co.uk/")
	session.get("https://ojp.nationalrail.co.uk/personal/member/welcome")
	session.get("https://ojp.nationalrail.co.uk/personal/omnibar/basket")
	response = session.post("https://ojp.nationalrail.co.uk/service/planjourney/plan", data = {
		"jpState": "1ingle" if is_return else "01ngle",
		"commandName": "journeyPlannerCommand",
		"from.searchTerm": from_station.get_name(),
		"to.searchTerm": to_station.get_name(),
		"timeOfOutwardJourney.arrivalOrDeparture": "ARRIVE" if arriving else "DEPART",
		"timeOfOutwardJourney.monthDay": when.strftime("%d/%m/%Y"),
		"timeOfOutwardJourney.hour": when.hour,
		"timeOfOutwardJourney.minute": when.minute,
		"checkbox": "true",
		"_checkbox": "on",
		"timeOfReturnJourney.arrivalOrDeparture": "ARRIVE" if return_arriving else "DEPART",
		"timeOfReturnJourney.monthDay": return_when.strftime("%d/%m/%Y"),
		"timeOfReturnJourney.hour": return_when.hour,
		"timeOfReturnJourney.minute": return_when.minute,
		"_showFastestTrainsOnly": "on",
		"numberOfAdults": adults,
		"numberOfChildren": children,
		"firstClass": "true",
		"_firstClass": "on",
		"standardClass": "true",
		"_standardClass": "on",
		"rcards": "",
		"numberOfEachRailcard": "0",
		"railcardCodes": "",
		"viaMode": "VIA",
		"via.searchTerm": "Station",
		"via1.searchTerm": "Station",
		"via2.searchTerm": "Station",
		"offSetOption": "0",
		"operator.code": "",
		"_reduceTransfers": "on",
		"_lookForSleeper": "on",
		"_directTrains": "on"
	})
	soup = bs4.BeautifulSoup(response.content, "html.parser")
	mtx_rows = soup.select("#oft .mtx")

	tickets = []
	for mtx_row in mtx_rows:
		price = 0
		name = "Ticket"
		provider = "Unknown"
		fare_breakdowns = [x.get("value").split("|") for x in mtx_row.select(".fare-breakdown input")]
		for fare_breakdown in fare_breakdowns:
			price += float(fare_breakdown[5])
			name = fare_breakdown[3]
			provider = fare_breakdown[11]
		journey_breakdown = mtx_row.select_one(".journey-breakdown input").get("value").split("|")

		tickets.append(Ticket(
			from_station,
			to_station,
			when.replace(hour = int(journey_breakdown[2].split(":")[0]), minute = int(journey_breakdown[2].split(":")[1])),
			when.replace(hour = int(journey_breakdown[5].split(":")[0]), minute = int(journey_breakdown[5].split(":")[1])),
			journey_breakdown[8],
			price,
			name,
			provider,
			"https://ojp.nationalrail.co.uk/service/timesandfares/" + from_station.get_code() + "/" + to_station.get_code() + "/" + when.strftime("%d%m%y") + "/" + when.strftime("%H%M") + "/" + ("arr" if arriving else "dep")
		))

	return tickets


def get_cheapest_ticket(from_station, to_station, time_date = None, arriving = False, is_return = False, return_time_date = None):
	tickets = get_tickets(from_station, to_station, time_date, arriving, is_return, return_time_date)
	tickets.sort(key = lambda tickets: tickets.get_price())
	print("Cheapest Ticket:\n")
	print(tickets[-1])
