import requests
import bs4
import re
import json

HEADERS = {
	"User-Agent": "ai-cw2 <https://github.com/dangee1705/ai-cw2>"
}

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
		return f"Station<{self.name}, {self.postcode}, {self.code}>"

	def __repr__(self):
		return str(self)

with open("data/stations.json", "w") as f:
	stations = []
	for letter in "ABCDEFGHIJKLMNOPQRSTUVWYXZ":
		url = f"https://en.wikipedia.org/wiki/UK_railway_stations_-_{letter}"
		response = requests.get(url, headers = HEADERS)
		soup = bs4.BeautifulSoup(response.content, "html.parser")
		rows = soup.select("table.wikitable>tbody>tr")
		for row in rows:
			data = [x.text.strip() for x in row.select("td")]
			if data and re.match("^[A-Z]{2}[0-9]{1,2} [0-9][A-Z]{2}$", data[1]) and data[-1]:
				stations.append({
					"name": data[0],
					"postcode": data[1],
					"code": data[-1][:3]
				})

	json.dump(stations, f)
