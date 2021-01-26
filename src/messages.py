def text(content):
	return {
		"type": "text",
		"content": content
	}

def ticket(ticket):
	return {
		"type": "ticket",
		"content": {
			"from_station": ticket.from_station.get_name(),
			"to_station": ticket.to_station.get_name(),
			"leave_at": ticket.leave_at,
			"arrive_at": ticket.arrive_at,
			"travel_time": ticket.travel_time,
			"no_of_changes": ticket.no_changes,
			"price": ticket.price,
			"name": ticket.name,
			"provider": ticket.provider,
			"link": ticket.link
		}
	}

def multiple_texts(texts):
	return [text(content) for content in texts]
	