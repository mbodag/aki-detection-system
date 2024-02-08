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
        hl7_message_str = 'MSH|^~\&|SENDING_APPLICATION|SENDING_FACILITY|RECEIVING_APPLICATION|RECEIVING_FACILITY|202302080945||ADT^A01|123456|P|2.3|PID|||123^^^Hospital&1||Doe^John||19800101|M|||123 Fake St.^^Metropolis^NY^12345^USA|||||||'
        message = self.parser.parse_message(hl7_message_str.split('|'))
        self.assertIsInstance(message, PatientAdmissionMessage)

    def test_parse_test_result_message(self):
        hl7_message_str = 'MSH|^~\&|LAB|Hospital|||202302081015||ORU^R01|789012|P|2.3|PID|||123^^^Hospital&1||Doe^John||19800101|M|||123 Fake St.^^Metropolis^NY^12345^USA|||||||OBR|1|||BLOOD^Blood Test|||202302080945|OBX|1|NM|CREAT^Creatinine||1.2|mg/dL|0.5-1.2|N|||F|||202302081015|'
        message = self.parser.parse_message(hl7_message_str.split('|'))
        self.assertIsInstance(message, TestResultMessage)

    def test_parse_discharge_message(self):
        hl7_message_str = 'MSH|^~\&|SENDING_APPLICATION|SENDING_FACILITY|RECEIVING_APPLICATION|RECEIVING_FACILITY|202302081130||ADT^A03|789012|P|2.3|PID|||123^^^Hospital&1||Doe^John||19800101|M|||123 Fake St.^^Metropolis^NY^12345^USA|||||||'
        message = self.parser.parse_message(hl7_message_str.split('|'))
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
