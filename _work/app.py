from flask import Flask, Response
from flask_cors import CORS
from flask import request, jsonify, json, url_for, send_file, abort,\
    redirect, make_response
# from teensy_driver import TeensyDriver
import picamera
import cv2
import socket
import io

#TODO:
## Add here the relevant code for the Depth camera
## Figure out how to send files, and put the appropiate wait times
##


app = Flask(__name__)
# td = TeensyDriver()
vc = cv2.VideoCapture(0)
CORS(app)



@app.route('/OL/set_velocity/<v1>/<v2>',methods=['GET'])
def set_velocities_OL(v1,v2):    
    v1,v2=float(v1),float(v2)    
    # td.set_velocities(v1,v2)
    return "Sent  %.2f %.2f"%(v1,v2)

@app.route('/stop_movement',methods=['GET'])
def stop_mov():
    print("got here yall") 
    return "stopped"   

def gen(): 
   """Video streaming generator function.""" 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')
               
@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/', methods=['GET'])
def index():
    return "Hello from RPi, you got it man"



if __name__ == "__main__":    
    print("Starting server..")
    app.run(host='0.0.0.0',port=5000)