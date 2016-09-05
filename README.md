1) To run the server the following command should be executed: 
    server.py [port]

    The default port is 2222.

    The URL of a server is localhost:port.

2) The API allows fetching data from a database. It can be accessed through /api.
    In order to run a query the "firstname", "lastname", "email" and "ops" parameters should be provided in the following fashion:

    http://localhost:2222/api?firstname=Jerry&lastname=Clarkson&email=jclarkson@startup.com&ops=%26%7C

    The "ops" parameter provides necessary AND and OR boolean operations for the query. 
    AND should be encoded as %26 (decodes to &).
    OR should be encoded as %7C (decodes to |).
    
    NOTE! The API considers the order of parameters provided. Thus, the following two queries will return different results:
    http://localhost:2222/api?email=jclarkson@startup.com&firstname=Jerry&lastname=Clarkson&ops=%26%7C (translates to WHERE email=jclarkson@startup.com AND firstname = Jerry OR lastname = Clarkson)
    http://localhost:2222/api?firstname=Jerry&lastname=Clarkson&email=jclarkson@startup.com&ops=%26%7C (translates to WHERE firstname = Jerry AND lastname = Clarkson OR email=jclarkson@startup.com)
    The relative position of the "ops" parameter in the query does not matter.

    Also, the various number of parameters can be provided. For example, the following queries will be valid:
    http://localhost:2222/api?firstname=Jerry&lastname=Clarkson&ops=%26
    http://localhost:2222/api?firstname=Jerry

#Update 1:
    Added support for JSON POST requests for the API.
    The "ops" property of the JSON object now defines boolean operators placed between parameters in the following strict order: "email" <op> "firstname" <op> "lastname".

    api_client.py allows to send simple JSON POST requests. 
   	Usage: api_client.py [--url server_url] --firstname FirstName --lastname LastName --ops BoolOperators  