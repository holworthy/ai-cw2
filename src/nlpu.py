import re
import spacy
import ticket_generator
from ticket_generator import Station, Ticket
import datetime
import messages
import random

nlp = spacy.load("en_core_web_lg")

class Ticket_Request:
	def __init__(self):
		self.from_station = None
		self.to_station = None
		self.time1 = datetime.datetime.now()
		self.dep_arr1 = False
		self.is_return = False
		self.time2 = None
		self.dep_arr2 = False
	
	def set_from_station(self, from_station):
		self.from_station = from_station

	def set_to_station(self, to_station):
		self.to_station = to_station

	def set_time1(self, time1):
		self.time1 = time1
	
	def set_dep_arr1(self, dep_arr1):
		self.dep_arr1 = dep_arr1
	
	def set_is_return(self, is_return):
		self.is_return = is_return
	
	def set_time2(self, time2):
		self.time2 = time2
	
	def set_dep_arr2(self, dep_arr2):
		self.dep_arr2 = dep_arr2
	
	def get_from_station(self):
		return self.from_station
	
	def get_to_station(self):
		return self.to_station
	
	def get_time1(self):
		return self.time1

	def get_dep_arr1(self):
		return self.dep_arr1
	
	def get_is_return(self):
		return self.is_return
	
	def get_time2(self):
		return self.time2
	
	def get_dep_arr2(self):
		return self.dep_arr2

def get_times(message):
	return [time[0] for time in re.findall("((([1-9])|([0-1][0-9])|(2[0-3])):(([0-5][0-9])))", message)]

def get_dates(message):
	dates = []
	for date in re.findall(r"(\d+/\d+/\d+)", message):
		dates.append(datetime.datetime.strptime(date, "%d/%m/%y"))
	return dates

state = "start"
ticket_request = Ticket_Request()

def message_is_yes(message):
	return message.lower() in ["yes", "yeah", "ye", "yee", "yep", "yes sir", "ok", "okay", "sure",	"sure thing", "sure thang", "yes i would", "yes please", "y"]

def message_is_no(message):
	return message.lower() in ["no", "noo", "nah", "neigh", "nope", "no sir", "no i wouldn't", "no i would not", "no thanks", "n"]

def ticket_from_ticket_request(ticket_request):
	return ticket_generator.get_cheapest_ticket(
		ticket_request.get_from_station(),
		ticket_request.get_to_station(), 
		ticket_request.get_time1(), 
		ticket_request.get_dep_arr1(), 
		ticket_request.get_is_return(), 
		ticket_request.get_time2(), 
		ticket_request.get_dep_arr2()
	)

def process_message(message, ticket_request):
	global state
	if state == "start":
		if message.lower() in ["hello", "hi", "hey", "sup"]:
			return [messages.text(random.choice(["Hey there", "How can I help?", "How's it going!"]))]
		elif message.lower() in ["I would like a train ticket"]:
			state = "from"
		else:
			state = "would_you_like_to_book"
			return messages.multiple_texts([
				"I'm sorry I'm not sure I know what you want.",
				"Would you like to book a ticket?"
			])
	elif state == "would_you_like_to_book":
		if message.lower() in ["yes", "yeah", "yep", "y", "sure", "okay"]:
			state = "from"
			return messages.multiple_texts([
				"Okay!",
				"Where would you like to go from?"
			])
	elif state == "from":
		# TODO: make this predictive and add a check
		from_station = Station.get_from_name(message)
		ticket_request.set_from_station(from_station)
		state = "to"
		return messages.multiple_texts(["Nice!", "Where would you like to go to?"])
	elif state == "to":
		# TODO: make this predictive and add a check
		to_station = Station.get_from_name(message)
		ticket_request.set_to_station(to_station)
		state = "when"
		return messages.multiple_texts(["Cool!", "When would you like that ticket for?"])
	elif state == "when":
		dates = get_dates(message)
		times = get_times(message)
		if len(dates) > 0:
			time = dates[0]
			timesplit = times[0].split(":")
			time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
		elif len(times) > 0:
			time = datetime.datetime.now()
			timesplit = times[0].split(":")
			time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
		ticket_request.set_time1(time)
		state = "arrive_depart_1"
		return messages.multiple_texts(["Nice!", "Is that arriving or departing?"])
	elif state == "arrive_depart_1":
		if any(x in message for x in ["Arriving", "arriving", "Ariving", "ariving"]):
			ticket_request.set_dep_arr1(True)
		state = "is_return"
		return messages.multiple_texts(["Nice!", "Is it a return?"])
	elif state == "is_return":
		if message_is_yes(message):
			ticket_request.set_is_return(True)
			state = "when_2"
			return messages.multiple_texts([
				"Okay",
				"When would you like the return for?"
			])
		elif message_is_no(message):
			ticket_request.set_is_return(False)
			state = "end"
			return [*messages.multiple_texts([
				"Alright then.",
				"Here is the cheapest ticket we could find",
			]), messages.ticket(ticket_from_ticket_request(ticket_request))]
		else:
			return messages.multiple_texts([
				"Sorry I'm not sure what you mean",
				"When would you like the return for?"
			])
	elif state == "when_2": 
		dates = get_dates(message)
		times = get_times(message)
		if len(dates) > 0:
			time = dates[0]
			timesplit = times[0].split(":")
			time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
		elif len(times) > 0:
			time = datetime.datetime.now()
			timesplit = times[0].split(":")
			time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
		ticket_request.set_time1(time)
		messages.multiple_texts(["Nice!", "Is that arriving or departing?"])
		state = "arrive_depart_2"
	elif state == "arrive_depart_2":
		if any(x in message for x in ["Arriving", "arriving", "Ariving", "ariving"]):
			ticket_request.set_dep_arr1(True)
			
		state = "end"
		return [*messages.multiple_texts(["Nice!", "Here is your ticket: "]), messages.ticket(ticket_from_ticket_request(ticket_request))]
	elif state == "end":
		return []
		#from_station, to_station, time_date, arriving, is_return, return_time_date, return_arriving
	
		
	# doc = nlp(message)

	# ticket_request = Ticket_Request()

	# # get Stations
	# for ent in doc.ents:
	# 	if "from " + str(ent) in message:
	# 		from_station_name = str(ent).title()
	# 	elif "to " + str(ent) in message:
	# 		to_station_name = str(ent).title()
	# ticket_request.set_from_station(ticket_generator.Station.get_from_name(from_station_name))
	# ticket_request.set_to_station(ticket_generator.Station.get_from_name(to_station_name)) 
	
	# # return check here

	# # get times and dates
	# dates = get_dates(message)
	# times = get_times(message)
	# if len(dates) > 0:
	# 	time = dates[0]
	# 	timesplit = times[0].split(":")
	# 	time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
	# elif len(times) > 0:
	# 	time = datetime.datetime.now()
	# 	timesplit = times[0].split(":")
	# 	time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
	# ticket_request.set_time1(time)

	# # get arriving
	# if not ticket_request.get_is_return() and ("Arriving" in message or "arriving"):
	# 	ticket_request.set_dep_arr1(True)

	# print(ticket_request.get_from_station(), ticket_request.get_to_station())

	# if not ticket_request.get_from_station() or not ticket_request.get_to_station():
	# 	return "I need to know where you are coming from and where you want to go to."

	# return str(ticket_generator.get_tickets(ticket_request.get_from_station(), ticket_request.get_to_station(), ticket_request.get_time1, ticket_request.get_dep_arr1, ticket_request.get_is_return(), ticket_request.get_time2()))
	return [messages.text("um thats awkward")]