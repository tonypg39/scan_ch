from flask import Flask, Response
from flask_cors import CORS
from flask import request, jsonify, json, url_for, send_file, abort,\
    redirect, make_response
import socket
import io
from camera import CameraToF

camera = None
app = Flask(__name__)
CORS(app)

@app.route('/capture', methods=['GET'])
def capture():
    global camera
    if camera is None:
        return {} # TODO: Make the Json empty response
    d = camera.capture()
    return json.dumps(d)

@app.route('/initialize', methods=['GET'])
def init():
    global camera
    camera = CameraToF()
    camera_details = camera.camDetails
    ##FIXME: Check if the object is Json parseable, otherwise, 
    ## you select the relevant fields and put in a dictionary.
    ## Intrinsics
    return json.dumps(camera_details)

    