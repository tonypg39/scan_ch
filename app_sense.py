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
    d = {}
    if camera is None:
        return json.dumps(d)
    resp = camera.capture()
    if resp["success"]:
        d["maps"] = camera.get_maps()
        d["params"] = camera.get_params()
    return json.dumps(d)

@app.route('/initialize', methods=['GET'])
def init():
    global camera
    camera = CameraToF()
    return json.dumps({"success": True})

if __name__ == "__main__":
    app.run("0.0.0.0")
    