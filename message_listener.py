import threading
import signal
import socket
import threading
import sys
from storage_manager import StorageManager
from message_parser import parse_message
from config import MLLP_PORT, MLLP_ADDRESS, PROMETHEUS_PORT, MESSAGE_LOG_CSV_PATH
import os
from hospital_message import PatientAdmissionMessage, TestResultMessage, PatientDischargeMessage
from alert_manager import AlertManager
import pandas as pd
import datetime
import time
import argparse

from prometheus_client import Gauge, Counter, Histogram, start_http_server

p_overall_messages_received = Gauge("overall_messages_received", "Number of overall messages received")
p_overall_messages_acknowledged = Counter("overall_messages_acknowledged", "Number of overall messages received")

p_invalid_message_parsing = Counter("invalid_message_parsing", "Number of invalid message types")

p_admission_messages = Counter("admission_messages_received", "Number of valid admission messages received")
# p_invalid_admission_messages does not exist

p_discharge_messages = Counter("discharge_messages_received", "Number of discharge messages received")
p_invalid_discharge_messages = Counter("invalid_discharge_messages_received", "Number of INVALID discharge messages received")

p_test_result_messages = Counter("test_result_messages_received", "Number of test result messages received")
p_unable_to_add_test_result = Counter("unable_to_add_test_result", "Number of cases where the test result was not added to the storage manager due to not having the patient in the current patients list")

p_positive_aki_predictions = Counter("positive_aki_predictions", "Number of positive aki predictions")
p_negative_aki_predictions = Counter("negative_aki_predictions", "Number of negative aki predictions")
p_number_of_pagings = Counter("number_of_pagings", "Number of times hospital staff has been paged")
p_failed_pagings = Counter("failed_pagings", "Number of times paging failed")

p_paging_latency = Histogram('paging_latency', 'Time to page positivie aki_prediction', buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 3, 4, 5, 10, 20, 40, 60, 120, 600, 1200])

p_message_latency = Histogram('message_latency', 'Time to process message', buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 3, 4, 5, 10, 20, 40, 60, 120, 600, 1200])

p_connection_closed_error = Counter("connection_closed_error", "Number of times socket connection closed")
p_message_errors = Counter("message_errors", "Number of times a message was badly handled")
start_http_server(PROMETHEUS_PORT)

shutdown_event = threading.Event()

def shutdown(s):
    shutdown_event.set()
    print("graceful shutdown")
    s.close()
    sys.exit(0)

# signal.signal(signal.SIGTERM, lambda *args: shutdown())

ACK = [
    "MSH|^~\&|||||20240129093837||ACK|||2.5",
    "MSA|AA",
]
MLLP_START_OF_BLOCK = 0x0b
MLLP_END_OF_BLOCK = 0x1c
MLLP_CARRIAGE_RETURN = 0x0d
HL7_MSA_ACK_CODE_FIELD = 1
HL7_MSA_ACK_CODE_ACCEPT = b"AA"


def parse_mllp_messages(buffer, source):
    i = 0
    messages = []
    consumed = 0
    expect = MLLP_START_OF_BLOCK
    while i < len(buffer):
        if expect is not None:
            if buffer[i] != expect:
                raise Exception(f"{source}: bad MLLP encoding: want {hex(expect)}, found {hex(buffer[i])}")
            if expect == MLLP_START_OF_BLOCK:
                expect = None
                consumed = i
            elif expect == MLLP_CARRIAGE_RETURN:
                messages.append(buffer[consumed+1:i-1])
                expect = MLLP_START_OF_BLOCK
                consumed = i + 1
        else:
            if buffer[i] == MLLP_END_OF_BLOCK:
                expect = MLLP_CARRIAGE_RETURN
        i += 1
    return messages, buffer[consumed:]

def initialise_system(message_log_filepath : str = MESSAGE_LOG_CSV_PATH):
    """
    Initialises the environment for the aki prediction system.
    """
    storage_manager = StorageManager(message_log_filepath = message_log_filepath)
    storage_manager.initialise_database(history_csv_path=HISTORY_CSV_PATH)

    alert_manager = AlertManager()
    
    return storage_manager, alert_manager

def to_mllp(segments: list):
    MLLP_START_OF_BLOCK = 0x0b
    MLLP_END_OF_BLOCK = 0x1c
    MLLP_CARRIAGE_RETURN = 0x0d
    m = bytes(chr(MLLP_START_OF_BLOCK), "ascii")
    m += bytes("\r".join(segments) + "\r", "ascii")
    m += bytes(chr(MLLP_END_OF_BLOCK) + chr(MLLP_CARRIAGE_RETURN), "ascii")
    return m

def send_ack(s: socket.socket):
    ACK = [f"MSH|^~\&|||||{datetime.datetime.now().strftime('%Y%M%D%H%M%S')}||ACK|||2.5",
                    "MSA|AA",]
    ack = to_mllp(ACK)
    s.sendall(ack[0:len(ack)//2])
    s.sendall(ack[len(ack)//2:])

def connect_to_socket(max_attempts = 10, sleep_time = 3):
    attempt = 1
    while attempt <= max_attempts:
        try:
            print(f"Attempting to connect to {MLLP_ADDRESS}:{MLLP_PORT}, Attempt {attempt}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((MLLP_ADDRESS, MLLP_PORT))
            print(f"Connected to {MLLP_ADDRESS}:{MLLP_PORT} successfully!")
            return s
        except socket.error as e:
            print(f"Connection attempt {attempt} failed:", e)
            attempt += 1
            if attempt <= max_attempts:
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:    
                sys.exit(f"Failed to connect to '{MLLP_ADDRESS}':{MLLP_PORT}. Exiting...")    
    
def from_mllp(buffer):
    return str(buffer[:-1], "ascii").split("\r") # Strip MLLP framing and final \r

def listen_for_messages(storage_manager: StorageManager, alert_manager: AlertManager):
    """
    This function listens for incoming MLLP messages, stores them, and sends AKI alerts if necessary.

    It continuously checks for new messages and processes them as they arrive. 
    The processing includes parsing the message, performing necessary actions based on the message content, 
    and sending an acknowledgment back to the sender.

    Raises:
        ConnectionError: If the function cannot establish a connection to the message source.
        MessageError: If there's an error in processing the message.

    Note:
        This function runs indefinitely until an external signal interrupts it or the program is terminated.
    """
    source = f"{MLLP_ADDRESS}:{MLLP_PORT}"
    buffer = b""
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s = connect_to_socket()    
    print(f"Listening for HL7 messages on '{MLLP_ADDRESS}':{MLLP_PORT}")
    while True:    
        received = []
        while len(received) < 1:
            try:
                r = s.recv(1024)
                if len(r) == 0:
                    p_connection_closed_error.inc()
                    s.close()
                    raise Exception("client closed connection")
            except ConnectionResetError:
                s = connect_to_socket()
                continue
            except Exception:
                s = connect_to_socket()
                continue
            
            buffer += r
            received, buffer = parse_mllp_messages(buffer, source)

            
        time_message_received = time.time()
        p_overall_messages_received.inc()
        try:
            message_object = parse_message(from_mllp(received[0]))
            if isinstance(message_object, PatientAdmissionMessage):
                storage_manager.add_admitted_patient_to_current_patients(message_object)
                p_admission_messages.inc()
                
            elif isinstance(message_object, TestResultMessage):
                storage_manager.add_test_result_to_current_patients(message_object)
                p_unable_to_add_test_result.inc()
            # If hospital staff has been previously paged about AKI in 
            # regards to that patient, do not do that again
                if storage_manager.no_positive_aki_prediction_so_far(message_object.mrn):
                    prediction_result = storage_manager.predict_aki(message_object.mrn)
                    if prediction_result == 1:
                        p_positive_aki_predictions.inc()
                        try:
                            alert_manager.send_alert(message_object.mrn, message_object.timestamp) 
                        except RuntimeError:
                            p_failed_pagings.inc()
                        p_number_of_pagings.inc()
                        time_latency_aki_paging = time.time() - time_message_received
                        p_paging_latency.observe(time_latency_aki_paging)
                        
                        storage_manager.update_positive_aki_prediction_to_current_patients(message_object.mrn)
                    elif prediction_result == 0:
                        p_negative_aki_predictions.inc()
            
                p_test_result_messages.inc()    
                
            elif isinstance(message_object, PatientDischargeMessage):
                storage_manager.remove_patient_from_current_patients(message_object)
                p_discharge_messages.inc()
            storage_manager.add_message_to_log_csv(message_object)
        except ValueError:
            p_message_errors.inc()
        finally: 
            send_ack(s)
            p_overall_messages_acknowledged.inc()
            time_message_latency = time.time() - time_message_received
            p_message_latency.observe(time_message_latency)
        signal.signal(signal.SIGTERM, lambda *args: shutdown(s))


            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AKI Prediction System')
    parser.add_argument('--history-dir', type=str, help='Path to history CSV file')
    args = parser.parse_args()

    if args.history_dir:
        HISTORY_CSV_PATH = args.history_dir
    else:
        from config import HISTORY_CSV_PATH

    storage_manager, alert_manager = initialise_system()
    listen_for_messages(storage_manager, alert_manager)