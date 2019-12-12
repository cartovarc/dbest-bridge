#!/usr/bin/python

from flask import Flask
from threading import Lock
import serial
import serial.tools.list_ports
import time
import threading
import six

# serial config
BAUDRATE = 9600

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
DEBUG_STATE_1 = '2'
DEBUG_STATE_2 = '3'
ALLOWED_MESSAGES = [
    PREPARE_EXCHANGER,
    DRON_IN,
    DRON_OUT,
    GET_STATE,
    DEBUG_LED,
    DEBUG_STATE_1,
    DEBUG_STATE_2,
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
NO_DATA = "NO_DATA"

lock = Lock()  # Lock for multiple requests
app = Flask(__name__)  # app for http server
freq_receive = 10 # try requests update per second DEBUG
ser = None

def get_port():
    global ser
    try:
        comports = serial.tools.list_ports.comports()
        if ser and len(comports) != 0:
            if not ser.is_open:
                ser.open()
            return ser
        if ser and len(comports) == 0:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.close()
            ser = None
        elif not ser and len(comports) != 0:
            device_name = comports[0].device
            ser = serial.Serial(device_name, timeout=0.2, baudrate = BAUDRATE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.open()
        elif not ser and len(comports) == 0:
            pass
        return ser
    except Exception:
        return None


def send_data(message):
    lock.acquire()
    print('MESSAGE TO SEND: ' + str(message))
    ser = get_port()
    #print('SERIAL PORT %s' % ser)
    result = None
    if ser:
        try:
            if six.PY2:
                ser.write(bytes(message)) # Python 2 syntax
            else:
                ser.write(bytes(message, 'utf-8')) # Python 3 syntax
            result = SENT
        except serial.SerialTimeoutException:
            result = TIMEOUT_ERROR
        except Exception as e:
            print(e)
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
            received_message = str(received_message.decode('utf-8'))
            result = received_message
        except Exception as e:
            print(e)
            result = INTERNAL_ERROR
    else:
        result = NO_SERIAL_PORT
    if result == '':
        result = NO_DATA
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
        if message == GET_STATE:
            result = send_and_receive(message)
        else:
            result = send_data(message)
        return result
    else:
        return FORBIDDEN_ERROR
    

def debug_read_buffer():
    time_0_last_cycle = time.time()
    while True:
        if time.time() >= time_0_last_cycle + 1.0/freq_receive:
            time_0_last_cycle = time.time()
            data = receive_data()
            print(data)


#thread = threading.Thread(target=debug_read_buffer, args=[])
#thread.daemon = True
#thread.start()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
