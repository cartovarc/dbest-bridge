#!/usr/bin/python

from flask import Flask
from threading import Lock
import serial
import serial.tools.list_ports
import time
import threading

# serial config
BAUDRATE = 9600
TIMEOUT = 0.1

PREPARE_EXCHANGER = 'PREPARE_EXCHANGER'
DRON_IN = 'DRON_IN'
DRON_OUT = 'DRON_OUT'
GET_STATE = 'GET_STATE'
SET_VALUES_INIT_BOTON = 'SET_VALUES_INIT_BOTON'
SET_VALUES_INIT_BATTERY = 'SET_VALUES_INIT_BATTERY'
SET_VALUES_INIT_SOCKET_COMMON = 'SET_VALUES_INIT_SOCKET_COMMON'
SET_VALUES_INIT_SOCKET_1 = 'SET_VALUES_INIT_SOCKET_1'
SET_VALUES_INIT_SOCKET_2 = 'SET_VALUES_INIT_SOCKET_2'
SET_VALUES_INIT_SOCKET_3 = 'SET_VALUES_INIT_SOCKET_3'
SET_VALUES_INIT_SOCKET_4 = 'SET_VALUES_INIT_SOCKET_4'
SET_VALUES_INIT_SOCKET_5 = 'SET_VALUES_INIT_SOCKET_5'
SET_VALUES_INIT_SOCKET_6 = 'SET_VALUES_INIT_SOCKET_6'
SET_VALUES_INIT_SOCKET_7 = 'SET_VALUES_INIT_SOCKET_7'
SET_VALUES_INIT_SOCKET_8 = 'SET_VALUES_INIT_SOCKET_8'
DEBUG_LED = '1'
DEBUG_STATE = '2'
ALLOWED_MESSAGES = [
    PREPARE_EXCHANGER,
    DRON_IN,
    DRON_OUT,
    GET_STATE,
    DEBUG_LED,
    DEBUG_STATE,
    SET_VALUES_INIT_BOTON,
    SET_VALUES_INIT_BATTERY,
    SET_VALUES_INIT_SOCKET_COMMON,
    SET_VALUES_INIT_SOCKET_1,
    SET_VALUES_INIT_SOCKET_2,
    SET_VALUES_INIT_SOCKET_3,
    SET_VALUES_INIT_SOCKET_4,
    SET_VALUES_INIT_SOCKET_5,
    SET_VALUES_INIT_SOCKET_6,
    SET_VALUES_INIT_SOCKET_7,
    SET_VALUES_INIT_SOCKET_8,
]
TIMEOUT_ERROR = 'TIMEOUT_ERROR'
INTERNAL_ERROR = 'INTERNAL_ERROR'
NO_SERIAL_PORT = 'NO_SERIAL_PORT'
FORBIDDEN_ERROR = 'FORBIDDEN_ERROR'
SENT = 'SENT'
LOST_UPDATE = "LOST_UPDATE"
MAX_TIME_WITHOUT_UPDATE = 5 #seconds

lock = Lock()  # Lock for multiple requests
app = Flask(__name__)  # app for http server
last_state = LOST_UPDATE
freq_receive = 30 # try requests update per second

def get_port():
    try:
        comports = serial.tools.list_ports.comports()
        device_name = comports[0].device
        ser = serial.Serial(device_name, BAUDRATE, timeout=TIMEOUT)
        return ser
    except Exception:
        return None


def send_data(message):
    lock.acquire()
    print('MESSAGE TO SEND: ' + str(message))
    ser = get_port()
    print('SERIAL PORT %s' % ser)
    result = None
    if ser:
        try:
            ser.write(bytes(message))
            result = SENT
        except serial.SerialTimeoutException:
            result = TIMEOUT_ERROR
        except Exception:
            result = INTERNAL_ERROR
    else:
        result = NO_SERIAL_PORT
    lock.release()
    return result


def receive_data():
    lock.acquire()
    ser = get_port()
    result = None
    if ser:
        try:
            received_message = ser.readline()
            received_message = received_message.decode('utf-8')
            result = received_message
        except Exception:
            result = INTERNAL_ERROR
    else:
        result = NO_SERIAL_PORT
    lock.release()
    return result


def send_and_receive(message):
    send_result = send_data(message)
    receive_result = receive_data()
    print('send_result: ' + str(send_result))
    print('receive_result: ' + str(receive_result))
    return receive_result


@app.route('/<message>')
def process_message(message):
    global last_state
    if message in ALLOWED_MESSAGES:
        if message == GET_STATE:
            return last_state
        result = send_data(message)
        return result
    else:
        return FORBIDDEN_ERROR


def read_state():
    global last_state
    time_0_last_update = time.time()
    time_0_last_cycle = time.time()
    while True:
        if time.time() >= time_0_last_cycle + 1.0/freq_receive:
            time_0_last_cycle = time.time()
            data = receive_data()
            if data != "":
                time_0_last_update = time.time()
                last_state = data
            elif time.time() >= time_0_last_update + MAX_TIME_WITHOUT_UPDATE:
                last_state = LOST_UPDATE
            print("current state: %s"%last_state)


thread = threading.Thread(target=read_state, args=[])
thread.daemon = True
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
