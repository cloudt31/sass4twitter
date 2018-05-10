import couchdb

admin = 'admin'
password = 'cloudt3118'
couchserver = couchdb.Server('http://%s:%s@115.146.86.187:5984/' % (admin, password))
