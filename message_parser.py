from hl7apy import parser
from hl7apy.exceptions import ParseException

class MessageParser:
    """
    MessageParser is responsible for parsing HL7 messages.
    """

    @staticmethod
    def parse_message(hl7_message_str):
        """
        Parse an HL7 message string into an HL7 message object.

        Parameters:
        hl7_message_str (str): A string representation of an HL7 message.

        Returns:
        HL7Message: An object representing the parsed HL7 message.
        """
        try:
            hl7_message = parser.parse_message(hl7_message_str)
            return hl7_message
        except ParseException as e:
            print(f"Failed to parse HL7 message: {e}")
            return None

    @staticmethod
    def extract_patient_info(hl7_message):
        """
        Extract patient information from the parsed HL7 message.

        Parameters:
        hl7_message (HL7Message): The parsed HL7 message object.

        Returns:
        dict: A dictionary containing patient information.
        """
        # Assuming HL7 v2.x message structure.
        # Extract patient information from the PID segment
        patient_info = {}
        if hl7_message and 'PID' in hl7_message:
            pid_segment = hl7_message.segment('PID')
            patient_info = {
                'patient_id': pid_segment.patient_id_internal_id[0].value,
                'patient_name': pid_segment.patient_name[0].value,
                'date_of_birth': pid_segment.date_time_of_birth.value,
                # Add other necessary fields
            }
        return patient_info

    @staticmethod
    def extract_test_results(hl7_message):
        """
        Extract test results from the parsed HL7 message.

        Parameters:
        hl7_message (HL7Message): The parsed HL7 message object.

        Returns:
        dict: A dictionary containing test results.
        """
        # Assuming HL7 v2.x message structure and OBX segments for observations.
        test_results = {}
        if hl7_message and 'OBX' in hl7_message:
            for obx in hl7_message.segments('OBX'):
                # OBX-3 is the Observation Identifier
                test_id = obx.observation_identifier[0].value
                # OBX-5 is the Observation Value
                test_value = obx.observation_value[0].value
                test_results[test_id] = test_value
        return test_results

# Example usage:
# hl7_message_str = '...HL7 message string...'
# parsed_message = MessageParser.parse_message(hl7_message_str)
# patient_info = MessageParser.extract_patient_info(parsed_message)
# test_results = MessageParser.extract_test_results(parsed_message)
