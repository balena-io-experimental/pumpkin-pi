import time
import cv2
import numpy as np

from flask import Flask, render_template, Response, request
app = Flask(__name__)

from picamera.array import PiRGBArray
from picamera import PiCamera

from motor import Motor
motor = Motor()

execfile('led.py')



camera = PiCamera(sensor_mode=1)
camera.framerate = 12
camera.resolution = (1280, 720)
rawCapture = PiRGBArray(camera, size=(1280, 720))

colorLower = (0, 0, 200)
colorUpper = (0, 0, 255)


# allow the camera to warmup
time.sleep(0.1)

@app.route('/motor')
def movedamotor():
    distance = request.args.get('dist')
    motor.set_angle(int(distance))
    return 'OK'

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        e1 = cv2.getTickCount()

        image = frame.array

        blurred = cv2.GaussianBlur(image, (11, 11), 0)
    	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, colorLower, colorUpper)
    	mask = cv2.erode(mask, None, iterations=2)
    	mask = cv2.dilate(mask, None, iterations=2)

    	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
    		cv2.CHAIN_APPROX_SIMPLE)
    	cnts = cnts[1]
    	center = None

    	# only proceed if at least one contour was found
    	if len(cnts) > 0:
    		# find the largest contour in the mask, then use
    		# it to compute the minimum enclosing circle and
    		# centroid
    		c = max(cnts, key=cv2.contourArea)
    		((x, y), radius) = cv2.minEnclosingCircle(c)
    		M = cv2.moments(c)
    		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    		# only proceed if the radius meets a minimum size
    		if radius > 5:
    			# draw the circle and centroid on the frame,
    			# then update the list of tracked points
    			cv2.circle(image, (int(x), int(y)), int(radius),
    				(0, 255, 255), 2)
    			cv2.circle(image, center, 5, (0, 0, 255), -1)

                xpos = float(center[0]) / 1280

                motor.set_angle(round(xpos*160))
                print(round(xpos*160))

        output_frame = cv2.imencode('.jpg', image)[1].tostring()
        rawCapture.truncate(0)

        e2 = cv2.getTickCount()
        time = (e2 - e1)/ cv2.getTickFrequency()
        print(time)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + output_frame + b'\r\n')



@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
