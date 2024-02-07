# test_storage_manager.py
import unittest
from unittest.mock import patch, MagicMock
from storage_manager import StorageManager
from hospital_message import PatientAdmissionMessage, PatientDischargeMessage, TestResultMessage

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.storage_manager = StorageManager()
        # Mock any necessary initial state here, such as the contents of creatine_results_history or current_patients.

    @patch('pandas.read_csv')
    def test_initialising_database(self, mock_read_csv):
        mock_read_csv.return_value = MagicMock()
        # Setup mock dataframe data here
        mock_read_csv.return_value.iterrows.return_value = iter([
            (0, {'mrn': '123', 'creatinine_result_0': '1.2', 'creatinine_result_1': '1.3'}),
        ])
        self.storage_manager.initialising_database()
        self.assertIn('123', self.storage_manager.creatine_results_history)
        self.assertEqual(self.storage_manager.creatine_results_history['123'], [1.2, 1.3])

    def test_add_admitted_patient_to_current_patients(self):
        self.storage_manager.creatine_results_history['123'] = [1.2, 1.3]
        admission_msg = PatientAdmissionMessage('123', 'John Doe', '1980-01-01', 'M', self.storage_manager)
        self.storage_manager.add_admitted_patient_to_current_patients(admission_msg)
        self.assertIn('123', self.storage_manager.current_patients)
        self.assertEqual(self.storage_manager.current_patients['123']['name'], 'John Doe')

    def test_add_test_result_to_current_patients(self):
        self.storage_manager.current_patients['123'] = {'creatinine_results': [1.2]}
        test_results_msg = TestResultMessage('123', '2021-01-01', '08:00', 1.4, self.storage_manager)
        self.storage_manager.add_test_result_to_current_patients(test_results_msg)
        self.assertIn(1.4, self.storage_manager.current_patients['123']['creatinine_results'])

    def test_remove_patient_from_current_patients(self):
        self.storage_manager.current_patients['123'] = {'creatinine_results': [1.2]}
        self.storage_manager.remove_patient_from_current_patients('123')
        self.assertNotIn('123', self.storage_manager.current_patients)

    @patch('csv.DictWriter')
    @patch('builtins.open', new_callable=MagicMock)
    def test_add_message_to_log_csv(self, mock_open, mock_dict_writer):
        test_msg = PatientAdmissionMessage('123', 'John Doe', '1980-01-01', 'M', self.storage_manager)
        self.storage_manager.add_message_to_log_csv(test_msg)
        mock_open.assert_called_once_with('message_log.csv', 'a', newline='')
        mock_dict_writer.return_value.writerow.assert_called()

    # Additional test methods for instantiate_messages_from_log and other functionality as necessary.

if __name__ == '__main__':
    unittest.main()
