import unittest
from unittest.mock import Mock

from hospital_message import PatientAdmissionMessage, PatientDischargeMessage, TestResultMessage

class HospitalMessageTest(unittest.TestCase):
    def setUp(self):
        self.storage_manager = Mock()
        self.aki_predictor = Mock()

    def test_patient_admission_message(self):
        admission_msg = PatientAdmissionMessage(mrn='123', name='John Doe', date_of_birth='1980-01-01', sex='M', storage_manager=self.storage_manager)
        self.assertEqual(admission_msg.mrn, '123')
        self.assertEqual(admission_msg.name, 'John Doe')
        self.assertEqual(admission_msg.date_of_birth, '1980-01-01')
        self.assertEqual(admission_msg.sex, 'M')
        self.storage_manager.add_message_to_log_csv.assert_called_once_with(admission_msg)
        self.storage_manager.add_admitted_patient_to_current_patients.assert_called_once_with(admission_msg)

    def test_patient_discharge_message(self):
        discharge_msg = PatientDischargeMessage(mrn='123', storage_manager=self.storage_manager)
        self.assertEqual(discharge_msg.mrn, '123')
        self.storage_manager.add_message_to_log_csv.assert_called_once_with(discharge_msg)
        self.storage_manager.update_patients_data_in_creatine_results_history.assert_called_once_with(discharge_msg)
        self.storage_manager.remove_patient_from_current_patients.assert_called_once_with(discharge_msg)

    def test_test_result_message(self):
        test_result_msg = TestResultMessage(mrn='123', test_date='2021-01-01', test_time='08:00', creatine_value=1.2,
                                            storage_manager=self.storage_manager, aki_predictor=self.aki_predictor)
        self.assertEqual(test_result_msg.mrn, '123')
        self.assertEqual(test_result_msg.test_date, '2021-01-01')
        self.assertEqual(test_result_msg.test_time, '08:00')
        self.assertEqual(test_result_msg.creatinine_value, 1.2)
        self.storage_manager.add_message_to_log_csv.assert_called_once_with(test_result_msg)
        self.storage_manager.add_test_result_to_current_patients.assert_called_once_with(test_result_msg)
        self.aki_predictor.predict_aki.assert_called_once_with(test_result_msg)

if __name__ == "__main__":
    unittest.main()
