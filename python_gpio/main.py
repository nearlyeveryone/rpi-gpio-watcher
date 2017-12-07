#!/usr/bin/env python3

import time
import pygame
from pygame.locals import *
import logging
import logging.handlers
import argparse
import sys
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
import ephem, datetime, pytz, os
import RPi.GPIO as GPIO
import pigpio

# logging
# Defaults
LOG_FILENAME = "/tmp/myservice.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

# location for sunrise/sunset calculations
MY_TIMEZONE = "America/Kentucky/Louisville"
MY_LONGITUDE = '-85.339544'  # +N
MY_LATITUDE = '38.355298' # +E
MY_ELEVATION = 253         # meters

# location config
pytz.timezone(MY_TIMEZONE)
here = ephem.Observer()
here.lat = MY_LATITUDE
here.lon = MY_LONGITUDE
here.elevation = MY_ELEVATION
here.horizon = '-12'

# GPIO config
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

# Door config
isDoorOpen = None
door_pin = [4, 5]
GPIO.setup(door_pin[0], GPIO.OUT)
GPIO.setup(door_pin[1], GPIO.OUT)
# Motor config
motor_pin = [20, 26]
GPIO.setup(motor_pin[0], GPIO.OUT)
GPIO.setup(motor_pin[1], GPIO.OUT)
GPIO.output(motor_pin[0], GPIO.LOW)
GPIO.output(motor_pin[1], GPIO.LOW)

# Servo config
servo_pwm_max = [1750, 2400]
servo_pwm_min = [750, 600]
servo_pin = [13, 19]

# pygame config
# pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.init() #turn all of pygame on.
if os.path.isfile('/home/pi/python_gpio/its-time-to-duel.wav'):
    sound = pygame.mixer.Sound('/home/pi/python_gpio/its-time-to-duel.wav')

pi = pigpio.pi()

if not pi.connected:
   raise EnvironmentError("Unable to enable servos!")


def is_daytime(sunrise_offset_minutes, sunset_offset_minutes):
    now = datetime.datetime.now()

    # Get the next sunrise/sunset
    next_sunrise = ephem.localtime(here.next_rising(ephem.Sun()))
    next_sunset = ephem.localtime(here.next_setting(ephem.Sun()))
    current = now.hour*60 + now.minute
    sunset = next_sunset.hour*60 + next_sunset.minute + int(sunset_offset_minutes)
    sunrise = next_sunrise.hour*60 + next_sunrise.minute + int(sunrise_offset_minutes)

    if (current > sunrise) and (current < sunset):
        return True
    else:
        return False


def close_door():
    GPIO.output(door_pin[0], GPIO.LOW)
    time.sleep(1)
    GPIO.output(door_pin[1], GPIO.HIGH)


def open_door():
    GPIO.output(door_pin[1], GPIO.LOW)
    time.sleep(1)
    GPIO.output(door_pin[0], GPIO.HIGH)


def split_params(params):
    equalities = params.split(';')
    d = dict()
    for e in equalities:
        s = e.split('=')
        if len(s) == 2:
            d[s[0].strip()] = s[1].strip()
    return d


class ControlModel(object):
    pass


def load_session():
    # dbPath = '/home/nearlyeveryone/WebApi.db'
    dbPath = '/home/pi/publish/WebApi.db'
    engine = create_engine('sqlite:///%s' % dbPath, echo=True)

    metadata = MetaData(engine)
    control_models = Table('ControlModels', metadata, autoload=True)
    mapper(ControlModel, control_models)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def automatic_door(control_model):
    print("doorcheck")
    print(control_model.Parameters)
    params = split_params(control_model.Parameters)
    global isDoorOpen

    day_time = is_daytime(params['sunriseOffset'], params['sunsetOffset'])

    if control_model.Value:
        if day_time and (not isDoorOpen or isDoorOpen is None):
            open_door()
            control_model.Status = 'Door opened at ' + datetime.datetime.strftime(datetime.datetime.now(), "%H:%M")
            isDoorOpen = True
        elif not day_time and (isDoorOpen or isDoorOpen is None):
            close_door()
            control_model.Status = 'Door closed at ' + datetime.datetime.strftime(datetime.datetime.now(), "%H:%M")
            isDoorOpen = False
    elif params['stateWhenOff'].upper() == 'OPEN':
        open_door()
        control_model.Status = 'Door is being forced open'
        isDoorOpen = True
    else:
        close_door()
        control_model.Status = 'Door being forced closed'
        isDoorOpen = False

    session.commit()


def move_camera(control_model):
    if control_model.Value:
        print(control_model.Parameters)
        params = split_params(control_model.Parameters)

        control_model.Status = 'Moving Servo'
        session.commit()

        servo_pwm_v = ((servo_pwm_max[0] - servo_pwm_min[0]) / 180) * int(params['verticalDegrees']) + servo_pwm_min[0]
        servo_pwm_h = ((servo_pwm_max[1] - servo_pwm_min[1]) / 180) * int(params['horizontalDegrees']) + servo_pwm_min[1]
        pi.set_servo_pulsewidth(servo_pin[0], servo_pwm_v)
        pi.set_servo_pulsewidth(servo_pin[1], servo_pwm_h)

        controlModel.Value = False
        control_model.Status = 'Idle'
        session.commit()



def feeder(control_model):
    if control_model.Value:
        sound.play(loops=2)
        print(control_model.Parameters)
        params = split_params(control_model.Parameters)

        control_model.Status = 'Currently Feeding'
        session.commit()

        GPIO.output(motor_pin[1], GPIO.HIGH)
        time.sleep(int(params['timeOn']))
        GPIO.output(motor_pin[1], GPIO.LOW)

        controlModel.Value = False
        control_model.Status = 'Idle'
        session.commit()


session = load_session()
while true:
    controlModels = session.query(ControlModel).all()
    for i, controlModel in enumerate(controlModels):
        if controlModel.Description == 'Automatic Door':
            automatic_door(controlModel)
        if controlModel.Description == 'Move Camera':
            move_camera(controlModel)
        if controlModel.Description == 'Feeder':
            feeder(controlModel)
    time.sleep(1)
