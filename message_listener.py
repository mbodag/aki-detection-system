
import socket
import simulator
import time
from storage_manager import StorageManager
from message_parser import MessageParser
from aki_predictor import AKIPredictor
from config import MLLP_PORT, MLLP_ADDRESS
from hospital_message import PatientAdmissionMessage, TestResultMessage, PatientDischargeMessage
from alert_manager import AlertManager
import pandas as pd


ACK = [
    "MSH|^~\&|||||20240129093837||ACK|||2.5",
    "MSA|AA",
]



def initialise_system():
    """
    Initialises the environment for the aki prediction system.
    """
    storage_manager = StorageManager()
    storage_manager.initialise_database()
    
    aki_predictor = AKIPredictor(storage_manager)

    message_parser = MessageParser()
    alert_manager = AlertManager()
    
    return storage_manager, aki_predictor, message_parser, alert_manager
    
    
def compute_f3_score(true_positives, false_positives, false_negatives):
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f3_score = (1 + 3**2) * (precision * recall) / (3**2 * precision + recall)
    return f3_score

def to_mllp(segments):
    m = bytes(chr(simulator.MLLP_START_OF_BLOCK), "ascii")
    m += bytes("\r".join(segments) + "\r", "ascii")
    m += bytes(chr(simulator.MLLP_END_OF_BLOCK) + chr(simulator.MLLP_CARRIAGE_RETURN), "ascii")
    return m

def from_mllp(buffer):
    return str(buffer[1:-3], "ascii").split("\r") # Strip MLLP framing and final \r

def listen_for_messages(storage_manager, aki_predictor, message_parser, alert_manager):
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
            
            # Be careful because we might store a message it then crash before acknowledging it (and so we'll receive it twice)
            
            # STORAGE STAGE
            if isinstance(message_object, PatientAdmissionMessage):
                storage_manager.add_admitted_patient_to_current_patients(message_object)
            elif isinstance(message_object, TestResultMessage):
                storage_manager.add_test_result_to_current_patients(message_object)
                prediction_result = aki_predictor.predict_aki(message_object.mrn)
                if prediction_result == 1:
                    alert_manager.send_alert(message_object.mrn)        
            elif isinstance(message_object, PatientDischargeMessage):
                storage_manager.remove_patient_from_current_patients(message_object)
            
            storage_manager.add_message_to_log_csv(message_object)
            ack = to_mllp(ACK)
            s.sendall(ack[0:len(ack)//2])
            s.sendall(ack[len(ack)//2:])
if __name__ == '__main__':
    storage_manager, aki_predictor, message_parser, alert_manager = initialise_system()
    listen_for_messages(storage_manager, aki_predictor, message_parser, alert_manager)