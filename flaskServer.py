from flask import Flask
from flask import request
from flask import render_template
from flask.ext.cors import CORS
import json

from srcdhall import getResponse

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def page():
    return render_template("index.html")

@app.route('/srcdhall')
# @cross_origin()
def srcdhall():
    state = request.args.get('state')
    text = request.args.get('text')
    paramsJson = request.args.get('params')
    params = json.loads(paramsJson)
    # params = request.headers.get('params', {})
    state, response, params = getResponse(state,text,params)
    dictResponse = {"state":state, "response":response, "params":params}
    jsonResponse = json.dumps(dictResponse, separators=(',',':'))
    return str(jsonResponse)

if __name__ == '__main__':
    app.debug = True
    app.run()