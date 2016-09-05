from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import parse_qs, parse_qsl
import sys, re, sqlite3, json, itertools

DB_NAME = 'database.db'
TABLE_NAME = 'feedback'
TABLE_PROP = '(firstname text, lastname text, email text, feedback text)'

class HTMLFormatter():
	def __init__(self):
		with open("header", "r") as h, open("footer", "r") as f:
			self.prefix = h.read()
			self.suffix = f.read()

	def wrap(self, body):
		return self.prefix + body + self.suffix


class RequestHandler(BaseHTTPRequestHandler):
	formatter = HTMLFormatter()
	conn = sqlite3.connect(DB_NAME) # open persistent connection to the database

	def _set_headers(self, c_type='text/html'):
		self.send_response(200)
		self.send_header('Content-type', c_type)
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	def validate(self, keys, post_dict):
		error_message = None
		for key in keys:
			#print key, key in post_dict
			if key in post_dict:
				value = post_dict[key].strip()

				if key == "firstname" or key == "lastname":
					if not value.isalpha():
						error_message = key + " should contain only alphabetic characters!"
				elif key == "feedback":
					if len(value) == 0:
						error_message = "The feedback has to be entered!"
				elif key == "email":
					if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
						error_message = "Email should follow the following format: abc@corp.com!"
				elif key == "ops":
					if not re.match(r"^[&|]*$", value):
						error_message = "Invalid ops found!"
					elif len(value) != len(keys)-2:
						error_message = "There should be " + str(len(keys)-2) + " operands!"
			else:
				error_message = "A required field " + key + " was not found in the request!" 

		return error_message

	def getOpWord(self, op):
		return "AND" if op=="&" else "OR"

	def retrieveFeedbackData(self, keys, post_dict):
		error_message = self.validate(keys+([] if len(keys) == 1 and "ops" not in post_dict else ["ops"]), post_dict)

		if len(keys) == 0:
			error_message = "There should be at least one query parameter."

		data = None
		if error_message is None:
			cur = RequestHandler.conn.cursor()
			ops = ""
			if len(keys) > 1:
				ops = post_dict["ops"].strip()


			cur.execute("SELECT * FROM " + TABLE_NAME + " WHERE "+keys[0]+"=? "+\
				"".join([self.getOpWord(ops[i])+" "+keys[i+1]+"=? " for i in xrange(len(ops))])+\
				"ORDER BY email", \
				tuple([post_dict[key].strip() for key in keys]))
			data = cur.fetchall()

		msg_data = {}
		msg_data["Success"] = error_message is None
		msg_data["Message"] = error_message
		msg_data["Data"] = data
		#print data

		return json.dumps(msg_data)

	def extract(self, post_dict):
		for key in post_dict.iterkeys():
			post_dict[key] = post_dict[key][0]

		return post_dict

	def do_GET(self):
		if self.path.startswith("/api?"):
			post_dict = self.extract(parse_qs(self.path[len("/api?"):]))
		
			keys = [item[0] for item in parse_qsl(self.path[len("/api?"):]) if item[0] != "ops"]

			msg = self.retrieveFeedbackData(keys, post_dict)

			# Send notification that the post request was processed
			self._set_headers(c_type="application/json")
			self.wfile.write(msg)			
		else:
			self._set_headers()
			with open("body", "r") as f: # allows to change form while the server is running
				self.wfile.write(RequestHandler.formatter.wrap(f.read()))

	def do_POST(self):
		if self.path == "/api" and self.headers["Content-Type"] == "application/json":
			post_dict = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
			keys = [key for key in ["email", "firstname", "lastname"] if key in post_dict]

			msg = self.retrieveFeedbackData(keys, post_dict)

			# Send notification that the post request was processed
			self._set_headers(c_type="application/json")
			self.wfile.write(msg)
		else:
			content_length = int(self.headers['Content-Length'])
			post_dict = self.extract(parse_qs(self.rfile.read(content_length)))
			#print post_dict
			keys = ("firstname", "lastname", "email", "feedback")
			error_message = self.validate(keys, post_dict)
		
			if error_message is None:
				# Store the data in DB
				cur = RequestHandler.conn.cursor()
				cur.execute("INSERT INTO " + TABLE_NAME + " VALUES (?, ?, ?, ?)", tuple([post_dict[key].strip() for key in keys]))
				RequestHandler.conn.commit()


			# Send notification that the post request was processed
			self._set_headers()
			with open("body", "r") as f: # allows to change form while the server is running
				self.wfile.write(RequestHandler.formatter.wrap(("Successfully updated the database!" if error_message is None else error_message)+f.read()))

def create_table(name, properties):
	conn = sqlite3.connect(DB_NAME)
	c = conn.cursor()

	c.execute('create table if not exists ' + name + ' ' + properties)
	c.close()
	conn.close()

if __name__ == "__main__":
	port = None
	if len(sys.argv) == 2 and sys.argv[1].isdigit():
		port = int(sys.argv[1])
	else:
		port = 2222

	create_table(TABLE_NAME, TABLE_PROP)
	server = HTTPServer(("", port), RequestHandler)
	#print "Server is running!"	
	server.serve_forever()

