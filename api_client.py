import json, urllib2, optparse, sys, itertools

if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option('--email', action="store", dest="email")
	parser.add_option('--firstname', action="store", dest="firstname")
	parser.add_option('--lastname', action="store", dest="lastname")
	parser.add_option('--ops', action="store", dest="ops")
	parser.add_option('--url', action="store", dest="url", default="http://localhost:2222/api")

	(options, args) = parser.parse_args(sys.argv)

	options = options.__dict__
	req_opts = ["url", "email", "firstname", "lastname", "ops"]
	for r_o in req_opts:
		if r_o not in options or options[r_o] is None:
			parser.error(r_o+ " has to be provided!")

	req = urllib2.Request(options["url"])
	del options["url"]
	req.add_header('Content-Type', 'application/json')

	response = urllib2.urlopen(req, json.dumps(options))
	print response.read()