from flask import Flask
from threading import Lock
import serial, serial.tools.list_ports, time, threading

# serial config
DEVICE_NAME = '/dev/ttyUSB' # it will update in update_device_name
BAUDRATE = 9600
TIMEOUT = 1
MAX_BYTES = 100

PREPARE_EXCHANGER = "PREPARE_EXCHANGER"
DRON_IN = "DRON_IN"
DRON_OUT = "DRON_OUT"
GET_STATE = "GET_STATE"
DEBUG_LED = "LED"
ALLOWED_MESSAGES = [PREPARE_EXCHANGER, DRON_IN, DRON_OUT, GET_STATE, DEBUG_LED]
TIMEOUT_ERROR = "TIMEOUT_ERROR"
INTERNAL_ERROR = "INTERNAL_ERROR"
COMMUNICATION_ERROR = "COMMUNICATION_ERROR"
FORBIDDEN_ERROR = "FORBIDDEN_ERROR"


lock = Lock() # Lock for multiple requests
app = Flask(__name__) # app for http server

def update_device_name():
    while True:
        try:
            comports = serial.tools.list_ports.comports()
            DEVICE_NAME = comports[0].device
        except Exception:
            DEVICE_NAME = None
        print(DEVICE_NAME)
        time.sleep(1)
        

thread = threading.Thread(target=update_device_name, args=[])
thread.daemon = True
thread.start()

def send_data(message):
    try:
        with serial.Serial(DEVICE_NAME, BAUDRATE, timeout=TIMEOUT) as ser:
            try:
                ser.write(bytes(message, "utf-8"))
            except serial.SerialTimeoutException:
                return TIMEOUT_ERROR
            except Exception:
                return INTERNAL_ERROR
    except Exception:
        return COMMUNICATION_ERROR

def receive_data():
    try:
        with serial.Serial(DEVICE_NAME, BAUDRATE, timeout=TIMEOUT) as ser:
            try:
                received_message = str(ser.read(MAX_BYTES))
                return receive_data
            except Exception:
                return INTERNAL_ERROR
    except Exception:
        return COMMUNICATION_ERROR

def send_and_receive(message):
    lock.acquire()
    send_result = send_data(message)
    receive_result = receive_data()
    lock.release()
    return receive_result


@app.route('/<message>')                                                                                                   
def process_message(message):
    if message in ALLOWED_MESSAGES:
        result = send_and_receive(message)
        return result
    else:
        return FORBIDDEN_ERROR


if __name__ == '__main__':
    app.run()
