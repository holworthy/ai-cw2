import flask
import time

app = flask.Flask(__name__)

@app.route("/")
def index():
	return flask.send_from_directory("templates/", "index.html")

@app.route("/message", methods = ["POST"])
def message():
	msg = flask.request.get_json()
	return "message"

app.run()