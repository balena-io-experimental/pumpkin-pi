import time
from threading import Thread
from sense_hat import SenseHat


def flicker():
    sense = SenseHat()

    X = [255, 200, 50]  # Red
    O = [0, 0, 0]  # White

    pattern = [
    X, X, X, X, O, O, X, O,
    X, X, X, X, O, X, O, O,
    X, X, X, X, X, O, O, X,
    X, X, X, X, O, O, X, O,
    O, O, X, O, O, X, O, O,
    O, X, O, O, X, O, O, X,
    X, O, O, X, O, O, X, O,
    O, O, X, O, O, X, O, O
    ]

    sense.set_pixels(pattern)

    while 1:
        sense.set_rotation(0)
        time.sleep(0.5)
        sense.set_rotation(270)
        time.sleep(0.5)
        sense.set_rotation(180)
        time.sleep(0.5)
        sense.set_rotation(90)
        time.sleep(0.5)

try:
    Thread(target=flicker, args=()).start()
except Excpetion, errtext:
    print errtext
