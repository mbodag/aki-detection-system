import pandas as pd
import json
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import HISTORY_CSV_PATH, DATABASE_URI
from hospital_message import PatientAdmissionMessage, TestResultMessage, PatientDischargeMessage

Base = declarative_base()

class PatientData(Base):
    """
    A database model to store patient MRN and creatinine results.
    """
    __tablename__ = 'patient_data'
    mrn = Column(String, primary_key=True)
    creatinine_results = Column(Text)  # Stores serialized list of creatinine results as a string

class StorageManager:
    """
    Manages storage and retrieval of patient data both in-memory and in a database.
    """
    def __init__(self):
        """
        Initializes the storage manager by setting up the database connection and sessionmaker.
        """
        self.engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.current_patients = {}
    
    def initialising_database(self):
        """
        Sets up the database by loading all patient data from a CSV file into it.
        """
        session = self.Session()
        df = pd.read_csv(HISTORY_CSV_PATH)
        for index, row in df.iterrows():
            # Extract only creatinine results, ignoring date columns
            creatinine_results = [row[col] for i, col in enumerate(df.columns) if "creatinine_result_" in col and not pd.isna(row[col])]
            
            # Serialize the list of creatinine results to a JSON string
            creatinine_results_str = json.dumps(creatinine_results)
            
            patient_data = PatientData(mrn=row['mrn'], creatinine_results=creatinine_results_str)
            session.merge(patient_data)  # Merge to handle updates to existing entries
        session.commit()
        session.close()

    def add_admitted_patient_to_dict(self, admission_msg):
        """
        Adds an admitted patient's data to the in-memory dictionary from the database.
        """
        session = self.Session()
        patient_data = session.query(PatientData).filter_by(mrn=admission_msg.mrn).first()
        if patient_data:
            creatinine_results = json.loads(patient_data.creatinine_results) if patient_data.creatinine_results else []
            self.current_patients[admission_msg.mrn] = {
                'date_of_birth': admission_msg.date_of_birth,
                'sex': admission_msg.sex,
                'creatinine_results': creatinine_results
            }
        else:
            self.current_patients[admission_msg.mrn] = {
                'date_of_birth': admission_msg.date_of_birth,
                'sex': admission_msg.sex,
                'creatinine_results': []
            }
        session.close()

    def add_test_result_to_database(self, test_results_msg):
        """
        Appends a new test result for a patient in the database.
        """
        session = self.Session()
        patient_data = session.query(PatientData).filter_by(mrn=test_results_msg.mrn).first()
        if patient_data:
            # Deserialize, append the new result, and serialize back to string
            creatinine_results = json.loads(patient_data.creatinine_results) if patient_data.creatinine_results else []
            creatinine_results.append(test_results_msg.creatine_value)
            patient_data.creatinine_results = json.dumps(creatinine_results)
            session.commit()
        session.close()

    def append_test_result_to_dict(self, mrn, test_results_msg):
        """
        Updates the in-memory storage with a new test result for a patient.
        """
        if mrn in self.current_patients:
            self.current_patients[mrn]['creatinine_results'].append(test_results_msg.creatine_value)

    def remove_patient_from_dict(self, mrn):
        """
        Removes a patient's information from the in-memory storage.
        """
        if mrn in self.current_patients:
            self.current_patients.pop(mrn, None)
            
if __name__ == "__main__":
    storage_manager = StorageManager()
    storage_manager.initialising_database()
    
    admission_msg = PatientAdmissionMessage(mrn='822825', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    storage_manager.add_admitted_patient_to_dict(admission_msg)
    print(storage_manager.current_patients)
    
    test_result_msg = TestResultMessage(mrn='822825', test_date='2021-01-01', test_time='08:00', creatine_value=1.2)
    storage_manager.add_test_result_to_database(test_result_msg)
    
    discharge_msg = PatientDischargeMessage(mrn='822825')
    storage_manager.remove_patient_from_dict(discharge_msg.mrn)
    print(storage_manager.current_patients)
    
    admission_msg = PatientAdmissionMessage(mrn='822825', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    storage_manager.add_admitted_patient_to_dict(admission_msg)
    print(storage_manager.current_patients)

    
    