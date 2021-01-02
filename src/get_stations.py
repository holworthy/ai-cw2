import requests
import bs4
import re
import json

HEADERS = {
	"User-Agent": "ai-cw2 <https://github.com/dangee1705/ai-cw2>"
}

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
