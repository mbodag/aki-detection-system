import unittest
from unittest.mock import Mock

# from hl7apy import parser
from hospital_message import PatientDischargeMessage, PatientAdmissionMessage, TestResultMessage
from message_parser import MessageParser

class MessageParserTest(unittest.TestCase):
    def setUp(self):
        self.storage_manager = Mock()
        self.aki_predictor = Mock()
        self.parser = MessageParser(self.storage_manager, self.aki_predictor)

    def test_parse_admission_message(self):
        hl7_message_str = '...ADT^A01 HL7 message string...'
        message = self.parser.parse_message(hl7_message_str)
        self.assertIsInstance(message, PatientAdmissionMessage)

    def test_parse_test_result_message(self):
        hl7_message_str = '...ORU^R01 HL7 message string...'
        message = self.parser.parse_message(hl7_message_str)
        self.assertIsInstance(message, TestResultMessage)

    def test_parse_discharge_message(self):
        hl7_message_str = '...ADT^A03 HL7 message string...'
        message = self.parser.parse_message(hl7_message_str)
        self.assertIsInstance(message, PatientDischargeMessage)

    def test_extract_patient_info(self):
        hl7_message = self.parser.parse_message("...")
        extracted_info = self.parser.extract_patient_info(hl7_message)
        self.assertIsInstance(extracted_info, dict)
        self.assertEqual(extracted_info["patient_id"], "PATIENT123")
        self.assertEqual(extracted_info["patient_name"], "Doe^John")
        self.assertEqual(extracted_info["date_of_birth"], "19800101")

    def test_extract_patient_info_no_pid(self):
        hl7_message = self.parser.parse_message("...n")
        extracted_info = self.parser.extract_patient_info(hl7_message)
        self.assertIsInstance(extracted_info, dict)
        self.assertEqual(extracted_info, {})

if __name__ == '__main__':
    unittest.main()