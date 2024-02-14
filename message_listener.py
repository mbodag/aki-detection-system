
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


def initialise_system(message_log_filepath : str = MESSAGE_LOG_CSV_PATH):
    """
    Initialises the environment for the aki prediction system.
    """
    storage_manager = StorageManager(message_log_filepath = message_log_filepath)
    storage_manager.initialise_database()
    
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
    return str(buffer[1:-3], "ascii").split("\r") # Strip MLLP framing and final \r

def listen_for_messages(storage_manager: StorageManager, aki_predictor: AKIPredictor, message_parser: MessageParser, alert_manager: AlertManager):
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((MLLP_ADDRESS, MLLP_PORT))
        print(f"Listening for HL7 messages on '{MLLP_ADDRESS}':{MLLP_PORT}")
        while True:
            buffer = s.recv(1024)
            if len(buffer) == 0:
                break
            messages.append(from_mllp(buffer))
            message_object = message_parser.parse_message(from_mllp(buffer))
                        
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
            ack = to_mllp(ACK)
            s.sendall(ack[0:len(ack)//2])
            s.sendall(ack[len(ack)//2:])
            
if __name__ == '__main__':
    storage_manager, aki_predictor, message_parser, alert_manager = initialise_system()
    listen_for_messages(storage_manager, aki_predictor, message_parser, alert_manager)