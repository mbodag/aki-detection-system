
import socket
from storage_manager import StorageManager
from message_parser import MessageParser
from aki_predictor import AKIPredictor
#from config import MLLP_PORT, MLLP_ADDRESS
import os
from hospital_message import PatientAdmissionMessage, TestResultMessage, PatientDischargeMessage
from alert_manager import AlertManager
import pandas as pd
from config import MESSAGE_LOG_CSV_PATH

MLLP_ADDRESS, MLLP_PORT = os.environ['MLLP_ADDRESS'].split(":")
MLLP_PORT = int(MLLP_PORT)

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
    storage_manager = StorageManager()
    storage_manager.initialise_database(message_log_filepath = message_log_filepath)
    
    aki_predictor = AKIPredictor(storage_manager)

    message_parser = MessageParser()
    alert_manager = AlertManager()
    
    return storage_manager, aki_predictor, message_parser, alert_manager
    

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

def listen_for_messages(storage_manager: StorageManager, aki_predictor: AKIPredictor, message_parser: MessageParser, alert_manager: AlertManager):
    i = 0
    buffer = b""
    messages = []
    source = f"{MLLP_ADDRESS}:{MLLP_PORT}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((MLLP_ADDRESS, MLLP_PORT))
        print(f"Listening for HL7 messages on '{MLLP_ADDRESS}':{MLLP_PORT}")
        while True:    
            received = []
            while len(received) < 1:
                r = s.recv(1024)
                if len(r) == 0:
                    raise Exception("client closed connection")
                buffer += r
                received, buffer = parse_mllp_messages(buffer, source)
    
            messages.append(from_mllp(received[0]))
            message_object = message_parser.parse_message(from_mllp(received[0]))
            if isinstance(message_object, PatientAdmissionMessage):
                storage_manager.add_admitted_patient_to_current_patients(message_object)
            elif isinstance(message_object, TestResultMessage):
                storage_manager.add_test_result_to_current_patients(message_object)
                prediction_result = aki_predictor.predict_aki(message_object.mrn)
                if prediction_result == 1:
                    alert_manager.send_alert(message_object.mrn, message_object.timestamp) 
            elif isinstance(message_object, PatientDischargeMessage):
                storage_manager.remove_patient_from_current_patients(message_object)
            

            storage_manager.add_message_to_log_csv(message_object)

            ACK = [
    f"MSH|^~\&|||||44444444||ACK|||2.5",
    "MSA|AA",
]
            ack = to_mllp(ACK)
            s.sendall(ack[0:len(ack)//2])
            s.sendall(ack[len(ack)//2:])
if __name__ == '__main__':
    storage_manager, aki_predictor, message_parser, alert_manager = initialise_system()
    listen_for_messages(storage_manager, aki_predictor, message_parser, alert_manager)