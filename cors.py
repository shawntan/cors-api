#!/usr/bin/env python
from flask import Flask, url_for, render_template, abort, Response
from pymongo import Connection
try:
	import simplejson as json
except ImportError:
	import json

app = Flask(__name__)

connection = Connection()
db = connection.corsdatabase

@app.route('/')
def main():
	return 'Hello World'

@app.route('/api/modules/', methods=['GET'])
def get_all_modules():
	"""Returns all the modules.
	"""
	entities = db['modules'].find()
	ls = []
	for e in entities:
		del e['_id']
		ls.append(e)
	return Response(json.dumps(ls), mimetype='application/json')

@app.route('/api/modules/<modulecode>', methods=['GET'])
def get_module(modulecode):
	"""Returns details for a specific module
	:params string modulecode
	"""
	entity = db['modules'].find_one({'code': modulecode})
	if not entity:
		abort(404, 'Module %s not found' % modulecode)
	del entity['_id'] # the _id object isn't JSON serializable
	return Response(json.dumps(entity), mimetype='application/json')

@app.route('/api/timetable/<modulecode>', methods=['GET'])
def get_module_time(modulecode):
	entity = db['modules'].find_one({'code': modulecode})
	if not entity:
		abort(404, 'Module %s not found' % modulecode)
	return Response(json.dumps({'lecture_time_table': entity['lecture_time_table']}),
		mimetype='application/json')

if __name__ == '__main__':
	app.run(debug=True)