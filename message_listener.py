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
import argparse

from prometheus_client import Gauge, Counter, start_http_server

p_overall_messages_received = Gauge("overall_messages_received", "Number of overall messages received")
p_overall_messages_acknowledged = Counter("overall_messages_acknowledged", "Number of overall messages received")
p_admission_messages = Counter("admission_messages_received", "Number of admission messages received")
p_discharge_messages = Counter("discharge_messages_received", "Number of discharge messages received")
p_test_result_messages = Counter("test_result_messages_received", "Number of test result messages received")
p_positive_aki_predictions = Counter("positive_aki_predictions", "Number of positive aki predictions")
p_aki_predictions_under_2_s = Counter("aki_under_2_s", "Number of aki predictions under 2 seconds")
p_aki_predictions_under_3_s = Counter("aki_under_3_s", "Number of aki predictions under 3 seconds")
p_aki_predictions_over_3_s = Counter("aki_over_3_s", "Number of aki predictions OVER 3 seconds")
start_http_server(PROMETHEUS_PORT)

shutdown_event = threading.Event()

def shutdown(s):
    shutdown_event.set()
    print("graceful shutdown")
    # s.close()
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
    messages = []
    source = f"{MLLP_ADDRESS}:{MLLP_PORT}"
    buffer = b""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((MLLP_ADDRESS, MLLP_PORT))
        print(f"Listening for HL7 messages on '{MLLP_ADDRESS}':{MLLP_PORT}")
        while True:    
            received = []
            while len(received) < 1:
                time_message_received = datetime.datetime.now()
                r = s.recv(1024)
                if len(r) == 0:
                    raise Exception("client closed connection")
                buffer += r
                received, buffer = parse_mllp_messages(buffer, source)
    
            messages.append(from_mllp(received[0]))
            message_object = parse_message(from_mllp(received[0]))
            p_overall_messages_received.inc()
            
            if isinstance(message_object, PatientAdmissionMessage):
                storage_manager.add_admitted_patient_to_current_patients(message_object)
                p_admission_messages.inc()
                
            elif isinstance(message_object, TestResultMessage):
                storage_manager.add_test_result_to_current_patients(message_object)
                # If hospital staff has been previously paged about AKI in 
                # regards to that patient, do not do that again
                if storage_manager.no_positive_aki_prediction_so_far(message_object.mrn):
                    prediction_result = storage_manager.predict_aki(message_object.mrn)
                    p_test_result_messages.inc()
                    if prediction_result == 1:
                        alert_manager.send_alert(message_object.mrn, message_object.timestamp) 
                        storage_manager.update_positive_aki_prediction_to_current_patients(message_object.mrn)
                        time_latency_aki_paging = datetime.datetime.now() - time_message_received
                        if time_latency_aki_paging.total_seconds() < 2:
                            p_aki_predictions_under_2_s.inc()
                        elif time_latency_aki_paging.total_seconds() < 3:
                            p_aki_predictions_under_3_s.inc()
                        else:
                            p_aki_predictions_over_3_s.inc()
                        p_positive_aki_predictions.inc()
                        
            elif isinstance(message_object, PatientDischargeMessage):
                storage_manager.remove_patient_from_current_patients(message_object)
                p_discharge_messages.inc()
            
            
            storage_manager.add_message_to_log_csv(message_object)

            ACK = [
    f"MSH|^~\&|||||{datetime.datetime.now().strftime('%Y%M%D%H%M%S')}||ACK|||2.5",
    "MSA|AA",
]
            ack = to_mllp(ACK)
            s.sendall(ack[0:len(ack)//2])
            s.sendall(ack[len(ack)//2:])
            p_overall_messages_acknowledged.inc()
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