#!/usr/bin/python

from flask import Flask
from threading import Lock
import serial
import serial.tools.list_ports
import time
import threading

# serial config
BAUDRATE = 9600
TIMEOUT = 0.5

PREPARE_EXCHANGER = 'PREPARE_EXCHANGER'
DRON_IN = 'DRON_IN'
DRON_OUT = 'DRON_OUT'
GET_STATE = 'GET_STATE'
DEBUG_LED = '1'
DEBUG_STATE = '2'
ALLOWED_MESSAGES = [
    PREPARE_EXCHANGER,
    DRON_IN,
    DRON_OUT,
    GET_STATE,
    DEBUG_LED,
    DEBUG_STATE,
]
TIMEOUT_ERROR = 'TIMEOUT_ERROR'
INTERNAL_ERROR = 'INTERNAL_ERROR'
NO_SERIAL_PORT = 'NO_SERIAL_PORT'
FORBIDDEN_ERROR = 'FORBIDDEN_ERROR'
SENT = 'SENT'

lock = Lock()  # Lock for multiple requests
app = Flask(__name__)  # app for http server


def get_port():
    try:
        comports = serial.tools.list_ports.comports()
        device_name = comports[0].device
        ser = serial.Serial(device_name, BAUDRATE, timeout=TIMEOUT)
        return ser
    except Exception:
        # print("NOT AVAILBLE DEVICES")
        return None


def send_data(message):
    lock.acquire()
    print('MESSAGE TO SEND: ' + str(message))
    ser = get_port()
    print('SERIAL PORT %s' % ser)
    result = None
    if ser:
        try:
            ser.write(bytes(message, 'utf-8'))
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
            received_message = str(ser.readline())
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
    if message in ALLOWED_MESSAGES:
        result = send_data(message)
        return result
    else:
        return FORBIDDEN_ERROR


def read_state():
    while True:
        data = receive_data()
        print('READ: ' + str(data))
        time.sleep(0.2)


thread = threading.Thread(target=read_state, args=[])
thread.daemon = True
thread.start()

if __name__ == '__main__':
    app.run()
