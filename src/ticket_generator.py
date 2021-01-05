import requests
import bs4
import re
import json
import datetime

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

class Ticket:
	def __init__(self, leave_at, arrive_at, no_changes, price, name, provider):
		self.leave_at = leave_at
		self.arrive_at = arrive_at
		self.travel_time = arrive_at - leave_at
		self.no_of_changes = no_changes
		self.price = price
		self.name = name
		self.provider = provider
	
	def __str__(self):
		return f"Ticket<{self.leave_at}, {self.arrive_at}, {self.travel_time}, {self.no_of_changes}, {self.price}, {self.name!r}, {self.provider!r}>"

	def __repr__(self):
		return str(self)



def get_tickets(from_station, to_station, time_date = None, arriving = False, is_return = False, return_time_date = None):
	if not time_date:
		time_date = datetime.datetime.now()
	try:
		stations = Station.get_stations()
		
		if is_return:
			# work this out 
			#ojp.nationalrail.co.uk/service/timesandfares/FROMSTATION/TOSTATION/DATE1/TIME1/DEP|ARR/DATE2/TIME2/DEP2|ARR2
			pass
		else:
			date1 = time_date.strftime("%d%m%y")
			time1 = time_date.strftime("%H%M")
			deparr1 = "arr" if arriving else "dep"
			url = f"https://ojp.nationalrail.co.uk/service/timesandfares/{from_station}/{to_station}/{date1}/{time1}/{deparr1}"
			response = requests.get(url)
			soup = bs4.BeautifulSoup(response.content, "html.parser")
			
			tickets = []
			for each in soup.select("#oft > tbody > tr.mtx"):
				fare = each.select_one(".fare-breakdown input[type=\"hidden\"]").get("value").split("|")[:-1]
				name = fare[2] + ", " + fare[3]
				price = fare[5]
				provider = fare[11]
				journey = each.select_one(".journey-breakdown input[type=\"hidden\"]").get("value").split("|")[:-1]
				leave = journey[2]
				leave = time_date.replace(hour= int(leave.split(":")[0]), minute= int(leave.split(":")[1]))
				arrive = journey[5]
				arrive = time_date.replace(hour= int(arrive.split(":")[0]), minute= int(arrive.split(":")[1]))
				if arrive - leave < datetime.timedelta(days=0):
					arrive = arrive.replace(day= arrive.day + 1)
				changes = journey[8]
				tickets.append(Ticket(leave, arrive, changes, price, name, provider))
				print(tickets[-1])
				
		return tickets
	except Exception as e:
		print(e)
		print("'stations.json' is Missing or Corrupted.")
		raise ValueError
	#ojp.nationalrail.co.uk/service/timesandfares/FROMSTATION/TOSTATION/DATE1/TIME1/DEP|ARR/DATE2/TIME2/DEP2|ARR2

get_tickets("NRW", "CRK", datetime.datetime.now())
