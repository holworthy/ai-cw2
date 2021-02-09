import datetime
import random
import re
from spellchecker import SpellChecker
import knn
import messages
import ticket_generator
from ticket_generator import Station, Ticket

spell = SpellChecker()
spell.word_frequency.load_words(station.get_name() for station in Station.get_stations())

class Ticket_Request:
	def __init__(self):
		self.from_station = None
		self.to_station = None
		self.time1 = None
		self.dep_arr1 = False
		self.is_return = False
		self.time2 = None
		self.dep_arr2 = False

		self.delay_from_station = None
		self.delay_to_station = None
		self.delay_current_station = Station.get_from_name("Ipswich")
	
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

def process_times_dates(message, ticket_request):
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
		if ticket_request.get_time1() != None and "next day" in message.lower():
			date_temp = ticket_request.get_time1()
			date_temp += datetime.timedelta(days=1)
			date_temp = date_temp.replace(hour = 9)
			dates.append(date_temp)
	return time, times, dates

def better_datetime_processing(message):
	dt = datetime.datetime.now()
	now = datetime.datetime.now()
	today = datetime.datetime(year = now.year, month = now.month, day = now.day)

	has_date_part = True
	has_time_part = True

	if "today" in message:
		dt = today
	elif "tomorrow" in message:
		dt = today + datetime.timedelta(days = 1)
	elif "in a week" in message or "a week today" in message:
		dt = today + datetime.timedelta(weeks = 1)
	elif "in a month" in message or "a month today" in message:
		dt = today + datetime.timedelta(months = 1)
	else:
		for i, day in enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
			if day in message.lower():
				days_ahead = i - dt.weekday()
				if days_ahead <= 0:
					days_ahead += 7
				dt = dt + datetime.timedelta(days_ahead)
				break
		else:
			match = re.match("([0-9]{2}/[0-9]{2}/[0-9]{4})|([0-9]{4}-[0-9]{2}-[0-9]{2})", message)
			if match:
				for pattern in ["%d/%m/%Y", "%Y-%m-%d"]:
					try:
						dt = datetime.datetime.strptime(match.group(0), pattern)
					except Exception as e:
						continue
					break
				else:
					raise ValueError("Invalid date")
			else:
				has_date_part = False

	if "morning" in message:
		dt = dt.replace(hour = 9, minute = 0)
	elif "afternoon" in message or "after lunch" in message:
		dt = dt.replace(hour = 14, minute = 0)
	elif "lunchtime" in message or "midday" in message:
		dt = dt.replace(hour = 12, minute = 0)
	else:
		match = re.match("[0-9]{2}:[0-9]{2}", message)
		if match:
			try:
				t = datetime.time.fromisoformat(match.group(0))
				dt = dt.replace(hour = t.hour, minute = t.minute, second = 0)
			except Exception as e:
				raise ValueError("Invalid time")
		else:
			for i in range(1, 12):
				if f"{i} am" in message or f"{i}am" in message:
					dt = dt.replace(hour = i, minute = 0, second = 0)
					break
				elif f"{i} pm" in message or f"{i}pm" in message:
					dt = dt.replace(hour = i + 12, minute = 0, second = 0)
					break
			else:
				if f"12 am" in message or f"12am" in message:
					dt = dt.replace(hour = 0, minute = 0, second = 0)
				elif f"12 pm" in message or f"12pm" in message:
					dt = dt.replace(hour = 12, minute = 0, second = 0)
				else:
					has_time_part = False
	
	if not has_date_part and not has_time_part:
		return None

	if not has_time_part:
		dt = dt.replace(hour = 9, minute = 0, second = 0)
	
	return dt

state = "start"

def message_is_yes(message):
	return message.lower() in ["yes", "yeah", "ye", "yee", "yep", "yes sir", "ok", "okay", "sure",	"sure thing", "sure thang", "yes i would", "yes please", "y"]

def message_is_no(message):
	return message.lower() in ["no", "noo", "nah", "neigh", "nope", "no sir", "no i wouldn't", "no i would not", "no thanks", "n"]

def ticket_from_ticket_request(ticket_request):
	print(ticket_request.get_from_station(),
		ticket_request.get_to_station(), 
		ticket_request.get_time1(), 
		ticket_request.get_dep_arr1(), 
		ticket_request.get_is_return(), 
		ticket_request.get_time2(), 
		ticket_request.get_dep_arr2())
	return ticket_generator.get_cheapest_ticket(
		ticket_request.get_from_station(),
		ticket_request.get_to_station(), 
		ticket_request.get_time1(), 
		ticket_request.get_dep_arr1(), 
		ticket_request.get_is_return(), 
		ticket_request.get_time2(), 
		ticket_request.get_dep_arr2()
	)

def get_current_state():
	return state

def process_message(message, ticket_request):
	message = " ".join(spell.correction(word) for word in message.split())
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
		elif "delay" in message.lower() or "late" in message.lower() or "behind" in message.lower() or "where is my train" in message.lower():
			state = "delay"
			return messages.multiple_texts([
				"Ok I just need some details to locate your train and predict the delay.",
				"What was the first station on the journey?"
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
		dt = better_datetime_processing(message)
		if not dt:
			return messages.multiple_texts(["Sorry I'm not sure what you mean", "When do you want the ticket for?"])
		else:
			ticket_request.set_time1(dt)
			state = "arrive_depart_1"
			return messages.multiple_texts(["Awesome!", "Is that arriving or departing?"])
	elif state == "arrive_depart_1":
		if any(x in message for x in ["Arriving", "arriving"]):
			ticket_request.set_dep_arr1(True)
		state = "is_return"
		return messages.multiple_texts(["Nice!", "Is it a return?"])
	elif state == "is_return":
		if message_is_yes(message):
			print("test 1")
			print(state)
			ticket_request.set_is_return(True)
			state = "when_2"
			return messages.multiple_texts([
				"Okay",
				"When would you like the return for?"
			])
		elif message_is_no(message):
			ticket_request.set_is_return(False)
			state = "start"
			try:
				return [*messages.multiple_texts([
					"Alright then.",
					"Here is the cheapest ticket we could find",
				]), messages.ticket(ticket_from_ticket_request(ticket_request))]
			except:
				return [*messages.multiple_texts([
					"There are no tickets at that time.",
					"Anything else I can help?"
					])]
		else:
			return messages.multiple_texts([
				"I'm sorry I don't understand.",
				"Is that a return? yes or no?"
			])
	elif state == "when_2":
		dt = better_datetime_processing(message)
		if not dt:
			return messages.multiple_texts(["Sorry I'm not sure what you mean", "When do you want the ticket for?"])
		else:
			ticket_request.set_time1(dt)
			state = "arrive_depart_2"
			return messages.multiple_texts(["Awesome!", "Is that arriving or departing?"])
	elif state == "arrive_depart_2":
		if any(x in message for x in ["Arriving", "arriving", "Ariving", "ariving"]):
			ticket_request.set_dep_arr1(True)
		state = "start"
		try:
			return [*messages.multiple_texts([
				"Alright then.",
				"Here is the cheapest tickets we could find",
			]), messages.ticket(ticket_from_ticket_request(ticket_request))]
		except:
			return [*messages.multiple_texts([
				"There are no tickets at those times.",
				"Anything else I can help?"
				])]
	elif state == "delay":
		ticket_request.delay_to_station = Station.get_from_name(message)
		if ticket_request.delay_to_station:
			state = "delay_2"
			return messages.multiple_texts(["Got it.", "And where is the last station in the journey?"])
		else:
			return messages.multiple_texts([
				"Sorry I'm not sure I know where that is",
				"Make sure you spelt that correctly and try again", 
				"Where would you like your journey to end?"
			])
	elif state == "delay_2":
		ticket_request.delay_from_station = Station.get_from_name(message)
		if ticket_request.delay_from_station:
			state = "start"
			now = datetime.datetime.now()
			now_plus_delay = now + datetime.timedelta(minutes = 10)
			delay = knn.predict_it(
				[now.year, now.month, now.day, knn.station_code_to_number(ticket_request.delay_from_station.get_code()), knn.station_code_to_number(ticket_request.delay_to_station.get_code()), knn.station_code_to_number(ticket_request.delay_current_station.get_code()), now.hour, now.minute, now_plus_delay.hour, now_plus_delay.minute],
				ticket_request.delay_from_station,
				ticket_request.delay_to_station
			)
			return messages.multiple_texts([
				"Got it.",
				f"Based on previous data, your train will probably arrive at its final destination {int(delay[0])} minutes late",
				"So it should arrive at " + (datetime.datetime.now() + datetime.timedelta(minutes = int(delay[0]))).strftime("%H:%M"),
				"Anything else I can help with?"])
		else:
			return messages.multiple_texts([
				"Sorry I'm not sure I know where that is",
				"Make sure you spelt that correctly and try again", 
				"Where would you like your journey to end?"])
	return [messages.text("um thats awkward")]
