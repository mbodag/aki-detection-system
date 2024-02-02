# storage_manager.py

import pandas as pd
from config import HOSPITAL_DATA_CSV_PATH

class LongTermStorageManager:
    """
    Manages long-term patient data storage.
    """
    
    @staticmethod
    def append_patient_data(patient_data):
        """
        Append new patient data to the hospital_data.csv.
        """
        # Load the CSV, append the data, and save it back.
        try:
            df = pd.read_csv(HOSPITAL_DATA_CSV_PATH)
            df = df.append(patient_data, ignore_index=True)
            df.to_csv(HOSPITAL_DATA_CSV_PATH, index=False)
        except Exception as e:
            log_error(str(e))

    @staticmethod
    def update_patient_data(patient_data):
        """
        Update existing patient data in hospital_data.csv.
        """
        # Implementation depends on how you identify records to update.
        pass

class ShortTermStorageManager:
    """
    Manages short-term patient data storage in memory.
    """
    current_patients = {}

    @classmethod
    def add_patient(cls, patient_mrn, patient_data):
        """
        Add new patient data to the current_patients dictionary.
        """
        cls.current_patients[patient_mrn] = patient_data

    @classmethod
    def remove_patient(cls, patient_mrn):
        """
        Remove a patient from the current_patients dictionary.
        """
        cls.current_patients.pop(patient_mrn, None)
