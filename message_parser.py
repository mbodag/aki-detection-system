from hospital_message import PatientDischargeMessage, PatientAdmissionMessage, TestResultMessage

class MessageParser:
    """
    MessageParser is responsible for parsing HL7 messages.
    """
    
    def __init__(self):
        pass
    
    def parse_message(self, hl7_message_str):
        """
        Parse an HL7 message string into an HL7 message object.

        Parameters:
        hl7_message_str (str): A string representation of an HL7 message.

        Returns:
        HL7Message: An object representing the parsed HL7 message.
        """
        message = hl7_message_str
        message_type = message[0].split("|")[8]
        if message_type == 'ADT^A01':
            patient_info = message[1].split("|")
            mrn = patient_info[3]
            name = patient_info[5]
            date_of_birth = patient_info[7]
            date_of_birth = patient_info[7][0:4]+"-"+patient_info[7][4:6]+"-"+patient_info[7][6:8]
            sex = patient_info[8]
            message_object = PatientAdmissionMessage(mrn, name, date_of_birth, sex)

        elif message_type == 'ORU^R01':
            mrn = message[1].split("|")[3]
            test_time = message[2].split("|")[7]
            test_day = test_time[:4]+"-"+test_time[4:6]+"-"+test_time[6:8]
            test_time = test_time[8:10]+":"+test_time[10:]
            test_result = message[3].split("|")[5]
            message_object = TestResultMessage(mrn, test_day, test_time, test_result)
            
        elif message_type == 'ADT^A03': 
            mrn = message[1].split("|")[3]
            message_object = PatientDischargeMessage(mrn)
            
        return message_object

#I think this can all just be deleted
#     @staticmethod
#     def extract_patient_info(hl7_message):
#         """
#         Extract patient information from the parsed HL7 message.

#         Parameters:
#         hl7_message (HL7Message): The parsed HL7 message object.

#         Returns:
#         dict: A dictionary containing patient information.
#         """
#         # Assuming HL7 v2.x message structure.
#         # Extract patient information from the PID segment
#         patient_info = {}
#         if hl7_message and 'PID' in hl7_message:
#             pid_segment = hl7_message.segment('PID')
#             patient_info = {
#                 'patient_id': pid_segment.patient_id_internal_id[0].value,
#                 'patient_name': pid_segment.patient_name[0].value,
#                 'date_of_birth': pid_segment.date_time_of_birth.value,
#                 # Add other necessary fields
#             }
#         return patient_info

#     @staticmethod
#     def extract_test_results(hl7_message):
#         """
#         Extract test results from the parsed HL7 message.

#         Parameters:
#         hl7_message (HL7Message): The parsed HL7 message object.

#         Returns:
#         dict: A dictionary containing test results.
#         """
#         # Assuming HL7 v2.x message structure and OBX segments for observations.
#         test_results = {}
#         if hl7_message and 'OBX' in hl7_message:
#             for obx in hl7_message.segments('OBX'):
#                 # OBX-3 is the Observation Identifier
#                 test_id = obx.observation_identifier[0].value
#                 # OBX-5 is the Observation Value
#                 test_value = obx.observation_value[0].value
#                 test_results[test_id] = test_value
#         return test_results

# # Example usage:
# # hl7_message_str = '...HL7 message string...'
# # parsed_message = MessageParser.parse_message(hl7_message_str)
# # patient_info = MessageParser.extract_patient_info(parsed_message)
# # test_results = MessageParser.extract_test_results(parsed_message)
