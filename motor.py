import RPi.GPIO as GPIO
import time
import math

class Motor:
    motor_outputs = [24,25,18,23]
    home_active = 4
    hold_position = True
    slew_speed = 60
    acceleration = 80
    steps_per_unit = 20
    steps_per_output_degree = 5.55 # 1.8 deg step motor, 5:1 reduction, half stepping means output is 0.18 degrees per half step
    current_angle = 80

    step_sequence = [
      [1,0,0,0],
      [1,1,0,0],
      [0,1,0,0],
      [0,1,1,0],
      [0,0,1,0],
      [0,0,1,1],
      [0,0,0,1],
      [1,0,0,1]
    ]
    current_step_position = 0 # retains the current position in the sequence for resume

    def __init__(self):
        # setup the GPIOs for output for the 4 motor connections
        GPIO.setmode(GPIO.BCM)

        for pin in self.motor_outputs:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        # setup the homing switch
        GPIO.setup(self.home_active, GPIO.IN)


    def step(self, direction='f'):
        # one step
        if direction == 'f':
            self.current_step_position = self.current_step_position + 1
            if self.current_step_position == len(self.step_sequence):
                self.current_step_position = 0
        else:
            self.current_step_position = self.current_step_position - 1
            if self.current_step_position == -1:
                self.current_step_position = len(self.step_sequence) - 1

        for pin in range(4):
            GPIO.output(self.motor_outputs[pin], self.step_sequence[self.current_step_position][pin])


    def move(self, steps, direction='f'):
        steps_done = 0

        A = self.acceleration * self.steps_per_unit
        acceleration_distance = (self.slew_speed * self.slew_speed * self.steps_per_unit * self.steps_per_unit) / (2 * A)
        if acceleration_distance >= steps / 2:
            acceleration_distance = steps / 2

        R = A / 1
        delay_period = float(1 / math.sqrt(2*A))

        while steps_done < steps:
            self.step(direction)
            steps_done = steps_done + 1

            if steps_done < acceleration_distance:
                delay_period = delay_period * (1 - R * delay_period * delay_period)
            elif steps_done >= (steps - acceleration_distance):
                delay_period = delay_period * (1 + R * delay_period * delay_period)

            time.sleep(delay_period)

        if self.hold_position == False:
            # make all outputs low to deenergise motor
            for pin in range(4):
                GPIO.output(self.motor_outputs[pin], 0)


    def move_degrees(self, degrees, direction='f'):
        # move the MOTOR specified number of degrees in the specified direction
        # translate degrees to steps and call move
        steps = round(degrees * self.steps_per_output_degree)
        self.move(steps, direction)


    def home_motor(self):
        self.current_angle = 80
        # keep moving the motor in a single direction until a switch is hit
        # from this we know the location of the output spindle
        # used in error and on powerup


    def set_angle(self, angle):
        # set the output angle
        # given that 0 is centered and we have a 160 degree camera, range should be between -80 and +80
        # remember that the output is driven by a 5:1 reduction
        # 160 deg is 0.44 revolutions of output, which means it needs 2.22 revolutions of the motor (1.8 deg per full step)
        # reduction means that output is 0.79 degrees per full step (0.395 per half)
        if angle < 0 or angle > 160:
            return False

        # find out where we are in relation to current angle and move to achieve desired angle
        difference = self.current_angle - angle

        # if negative, go reverse
        if difference < 0:
            self.move_degrees(abs(difference), 'r')
        else:
            self.move_degrees(difference, 'f')

        self.current_angle = angle
