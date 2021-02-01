import re
import spacy
import ticket_generator
from ticket_generator import Station, Ticket
import datetime
import messages
import random
from spellchecker import SpellChecker

nlp = spacy.load("en_core_web_lg")
spell = SpellChecker()
spell.word_frequency.load_words(station.get_name() for station in Station.get_stations())

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
	return [datetime.datetime.strptime(time[0], "%H:%M") for time in re.findall("((([1-9])|([0-1][0-9])|(2[0-3])):(([0-5][0-9])))", message)]

def get_dates(message):
	dates = []
	for date in re.findall(r"(\d+/\d+/\d+)", message):
		dates.append(datetime.datetime.strptime(date, "%d/%m/%y"))
	return dates

state = "start"

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
	print(message)
	message = " ".join(spell.correction(word) for word in message.split())
	print(message)

	global state
	if state == "start":
		if message.lower() in ["hello", "hi", "hey", "sup"]:
			return messages.multiple_texts(["Hey There!", "How can I help?"])
		elif "train" in message.lower() or "ticket" in message.lower():
			state = "from"
			return messages.multiple_texts([
				"Okay!",
				"Where would you like to go from?"
			])
		else:
			state = "would_you_like_to_book"
			return messages.multiple_texts([
				"I'm sorry I'm not sure I know what you want.",
				"Would you like to book a ticket?"
			])
	elif state == "would_you_like_to_book":
		if message_is_yes(message):
			state = "from"
			return messages.multiple_texts([
				"Okay!",
				"Where would you like to go from?"
			])
		elif message_is_no(message):
			state = "start"
			return messages.multiple_texts(["Ok, Have a nice day! 😊🚂"])
		else:
			return messages.multiple_texts([
				"I'm sorry, I don't understand",
				"Would you like to book a ticket?"
			])
	elif state == "from":
		from_station = Station.get_from_name(message)
		if from_station:
			ticket_request.set_from_station(from_station)
			state = "to"
			return messages.multiple_texts(["Nice!", "Where would you like to go to?"])
		else:
			return messages.multiple_texts(["Sorry I'm not sure I know where that is", "Make sure you spelt that correctly and try again", "Where would you like your journey to start?"])
	elif state == "to":
		to_station = Station.get_from_name(message)
		if to_station:
			ticket_request.set_to_station(to_station)
			state = "when"
			return messages.multiple_texts(["Cool!", "When would you like that ticket for?"])
		else:
			return messages.multiple_texts(["Sorry I'm not sure I know where that is", "Make sure you spelt that correctly and try again", "Where would you like your journey to end?"])
	elif state == "when":
		dates = get_dates(message)
		times = get_times(message)
		time = None
		if not dates or not times:
			if "tomorrow" in message.lower():
				print("boo")
				date_temp = datetime.datetime.now()
				date_temp += datetime.timedelta(days=1)
				date_temp = date_temp.replace(hour = 9)
				dates.append(date_temp)
			if "morning" in message.lower():
				time_temp = datetime.datetime.now()
				time_temp = time_temp.replace(hour=9, minute=0)
				if not dates:
					if time_temp < datetime.datetime.now():
						time_temp += datetime.timedelta(days=1)
					time = time_temp
				else:
					times.append(time_temp)
			if "evening" in message.lower():
				time_temp = datetime.datetime.now()
				time_temp = time_temp.replace(hour=17, minute=0)
				if not dates:
					if time_temp < datetime.datetime.now():
						time_temp += datetime.timedelta(days=1)
					time = time_temp
				else:
					times.append(time_temp)
			if "in an hour" in message.lower() or "in 1 hour" in message.lower():
				time_temp = datetime.datetime.now()
				time_temp += datetime.timedelta(hours=1)
				if not dates:
					time = time_temp
				else:
					times.append(time_temp)
		if time or dates or time:
			if not time and dates and times:
				time = dates[0]
				time = time.replace(hour=times[0].hour, minute=times[0].minute)
			if not time and not dates and times:
				time = datetime.datetime.now()
				time = time.replace(hour=times[0].hour, minute=times[0].minute)
			if not time and dates and not times:
				time = dates[0]
				if time.hour != 9:
					time = time.replace(hour=9)
			ticket_request.set_time1(time)
			if "arrive" in message.lower() or "arriving" in message.lower():
				ticket_request.set_dep_arr1(True)
				state = "is_return"
			elif "depart" in message.lower() or "departing" in message.lower():
				ticket_request.set_dep_arr1(False)
				state = "is_return"
			else:
				state = "arrive_depart_1"
		else:
			return messages.multiple_texts([
				"I'm sorry I didn't understand that time.",
				"What time would you like that train for?"
			])
		return messages.multiple_texts(["Nice!", "Is that arriving or departing?"])
		
	elif state == "arrive_depart_1":
		if any(x in message for x in ["Arriving", "arriving"]):
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
			state = "start"
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
	
	return [messages.text("um thats awkward")]
