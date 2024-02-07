import unittest
from unittest.mock import Mock

from datetime import datetime
import numpy as np

from aki_predictor import AKIPredictor

class AKIPredictorTest(unittest.TestCase):
    def setUp(self):
        self.storage_manager = Mock()
        self.test_mrn = '12345'
        self.test_patient_data = {
            'sex': 'f',
            'date_of_birth': '1990-01-01',
            'creatinine_results': [60.7, 62.3, 53, 80, 165, 204.56]
        }
        self.storage_manager.current_patients = {
            self.test_mrn: self.test_patient_data
        }

    def test_predict_aki(self):
        model_mock = Mock()
        model_mock.predict.return_value = np.array([1], dtype=np.int64)
        predictor = AKIPredictor(self.storage_manager)
        predictor.model = model_mock

        result = predictor.predict_aki(self.test_mrn)

        self.assertEqual(result, 1)
        model_mock.predict.assert_called_once_with

if __name__ == '__main__':
    unittest.main()