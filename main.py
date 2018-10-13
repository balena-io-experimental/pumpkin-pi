import time
import cv2
import numpy as np

from flask import Flask, render_template, Response, request
app = Flask(__name__)

from picamera.array import PiRGBArray
from picamera import PiCamera

from motor import Motor
motor = Motor()



camera = PiCamera()
camera.framerate = 30
camera.resolution = (400, 304)
rawCapture = PiRGBArray(camera, size=(400, 304))

# faceCascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
# hog = cv2.HOGDescriptor()
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

greenLower = (0, 0, 200)
greenUpper = (0, 0, 255)


# allow the camera to warmup
time.sleep(0.1)

@app.route('/motor')
def movedamotor():
    distance = request.args.get('dist')
    motor.set_angle(int(distance))
    return 'OK'

# @app.route('/')
# def image():
#     rawCapture.truncate(0)
#
#     camera.capture(rawCapture, format="bgr")
#     image = rawCapture.array
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     faces = faceCascade.detectMultiScale(gray, 1.3, 6)
#
#     for (x, y, w, h) in faces:
#         cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
#
#     cv2.imwrite('static/sample.png', image);
#     return '<img src="static/sample.png"/>'



@app.route('/')
def index():
    return render_template('index.html')

def gen():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        image = frame.array

        blurred = cv2.GaussianBlur(image, (11, 11), 0)
    	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, greenLower, greenUpper)
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

                xpos = float(center[0]) / 400

                motor.set_angle(round(xpos*160))

        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #
        # faces = faceCascade.detectMultiScale(gray, 1.3, 6)

        # (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
		#                                         padding=(8, 8), scale=1.05)
        #
        # for (x, y, w, h) in rects:
        #     cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
        #
    	# rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    	# pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    	# draw the final bounding boxes
    	# for (xA, yA, xB, yB) in faces:
    	# 	cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

        output_frame = cv2.imencode('.jpg', image)[1].tostring()
        rawCapture.truncate(0)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + output_frame + b'\r\n')



@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


# GpioPins = [24,25,17,23]

# step_sequence = [
#   [1,0,0,0],
#   [1,1,0,0],
#   [0,1,0,0],
#   [0,1,1,0],
#   [0,0,1,0],
#   [0,0,1,1],
#   [0,0,0,1],
#   [1,0,0,1]
# ]

# for i in range(512):
#   for halfstep in range(8):
#     for pin in range(4):
#       GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
#     time.sleep(0.001)

# main loop:
# take frame from camera
# analyse for body sized objects
# initiate tracker(s) on discovered object(s)
# pick one object to follow, and retain that one until it is lost from frame (to prevent jumping between objects)
# use the position of the center of the object in the image to map to the range of motion of the stepper
# update the stepper location to align with the object
