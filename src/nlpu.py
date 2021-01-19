import re
import spacy
import ticket_generator
import datetime

nlp = spacy.load("en_core_web_lg")

def get_times(message):
    return [time[0] for time in re.findall("((([1-9])|([0-1][0-9])|(2[0-3])):(([0-5][0-9])))", message)]

def get_dates(message):
    dates = []
    for date in re.findall(r"(\d+/\d+/\d+)", message):
        dates.append(datetime.datetime.strptime(date, "%d/%m/%y"))
    return dates

def process_message(message):
    doc = nlp(message)

    from_station_name = None
    to_station_name = None

    for ent in doc.ents:
        index = message.index(str(ent))
        if "from " + str(ent) in message:
            from_station_name = str(ent).title()
        elif "to " + str(ent) in message:
            to_station_name = str(ent).title()
    dates = get_dates(message)
    times = get_times(message)

    time = None
    if len(dates) > 0:
        time = dates[0]
        timesplit = times[0].split(":")
        time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
    elif len(times) > 0:
        time = datetime.datetime.now()
        timesplit = times[0].split(":")
        time = time.replace(hour= int(timesplit[0]), minute= int(timesplit[1]))
    from_station = ticket_generator.Station.get_from_name(from_station_name)
    to_station = ticket_generator.Station.get_from_name(to_station_name)

    print(from_station, to_station)

    if not from_station or not to_station:
        return "I need to know where you are coming from and where you want to go to."

    return str(ticket_generator.get_tickets(from_station, to_station, time))
