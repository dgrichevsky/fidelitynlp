from flask import Flask, render_template, request
import os, sys
from flask_cors import CORS, cross_origin
from flask import jsonify

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import engine
import database

app = Flask(__name__)
app.debug = True
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

@app.route('/', methods = ['POST', 'GET'])
def render():
    return 'NLP Engine Flask Microservice'

@app.route('/buildmodel', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def buildModel():
	return jsonify(engine.new_model(request.data))

@app.route('/delete', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def delete():
	return(database.delete_model(request.data))

@app.route('/getmodels', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def getmodels():
	return(database.get_models())

@app.route('/editmodel', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def editModel():
	return jsonify(engine.edit_model(request.data))

@app.route('/applymodel', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def applyModel():
	return engine.apply_model(request.data)

@app.route('/viewmodel', methods = ['POST', 'GET'])
@cross_origin(origin='*')
def viewModel():
	return jsonify(engine.view_model(request.data))

app.run()
#FLASK_APP=app.py FLASK_DEBUG=1 flask run
#https://flask-cors.readthedocs.io/en/v1.7.4/