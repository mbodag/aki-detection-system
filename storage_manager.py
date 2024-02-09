import csv
from datetime import datetime
import pandas as pd
import os
from config import HISTORY_CSV_PATH, MESSAGE_LOG_CSV_PATH
from hospital_message import PatientAdmissionMessage, TestResultMessage, PatientDischargeMessage

class StorageManager:
    """
    Manages storage and retrieval of patient data both in-memory and in a database.
    """
    def __init__(self):
        """
        Initializes the storage manager by setting up the database connection and sessionmaker.
        """
        # Stores creatine results for all patients
        # The file history.csv is imported and the data is stored in this dictionary
        # The key is the MRN and the value is a list of creatine results as floats
        # We only write to the creatine_results_history when a patient is discharged
        self.creatine_results_history = dict()
        
        
        # Stores data for patients currently admitted in the hospital
        # The key is the MRN and the value is a dictionary containing patient information
        # Entries are added when a patient is admitted and removed when a patient is discharged
        self.current_patients = dict()
    
    def initialise_database(self, message_log_filepath = MESSAGE_LOG_CSV_PATH):
        # Read the history.csv file to populate the creatine_results_history dictionary
        with open(HISTORY_CSV_PATH, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header row
            for row in reader: 
                mrn = row[0]
                creatine_results = [row[col] for col in range(2, len(row), 2) if row[col] != ""]
                creatine_results = list(map(float, creatine_results))
                self.creatine_results_history[mrn] = creatine_results
        
        self.instantiate_all_past_messages_from_log()
        
    def add_admitted_patient_to_current_patients(self, admission_msg):
        """
        Adds an admitted patient's data to the current_patients dictionary.
        """
        if admission_msg.mrn in self.creatine_results_history:
            self.current_patients[admission_msg.mrn] = {
                'name': admission_msg.name,
                'date_of_birth': admission_msg.date_of_birth,
                'sex': admission_msg.sex,
                'creatinine_results': self.creatine_results_history[admission_msg.mrn]
                }
                
        else:
            self.current_patients[admission_msg.mrn] = {
                'name': admission_msg.name,
                'date_of_birth': admission_msg.date_of_birth,
                'sex': admission_msg.sex,
                'creatinine_results': []
                }
    
    def add_test_result_to_current_patients(self, test_results_msg):
        """
        Appends a new test result for a patient in the in-memory dictionary.
        """
        if test_results_msg.mrn in self.current_patients:
            self.current_patients[test_results_msg.mrn]['creatinine_results'].append(float(test_results_msg.creatine_value))
        else:
            raise ValueError(f"Patient {test_results_msg.mrn} not found in current patients.")
            
    def remove_patient_from_current_patients(self, discharge_msg):
        """
        Removes a patient's information from the in-memory storage.
        """
        if discharge_msg.mrn in self.current_patients:
            self.current_patients.pop(discharge_msg.mrn, None)
        else:
            raise ValueError(f"Patient {discharge_msg.mrn} not found in current patients.")
        
    def update_patients_data_in_creatine_results_history(self, discharge_msg):
        """
        Updates the creatine results history for a discharged patient.
        """
        self.creatine_results_history[discharge_msg.mrn] = self.current_patients[discharge_msg.mrn]['creatinine_results']
    
    def add_message_to_log_csv(self, message):
        """
        Appends a message to message_log.csv.
        """
        # Define the fields for CSV logging
        fields = ['timestamp', 'type', 'mrn', 'additional_info']
        
        # Prepare the message data based on the type of message
        if isinstance(message, PatientAdmissionMessage):
            row_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'PatientAdmission',
                'mrn': message.mrn,
                'additional_info': f"Name: {message.name}. DOB: {message.date_of_birth}. Sex: {message.sex}"
            }
        elif isinstance(message, PatientDischargeMessage):
            row_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'PatientDischarge',
                'mrn': message.mrn,
                'additional_info': ''
            }
        elif isinstance(message, TestResultMessage):
            row_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'TestResult',
                'mrn': message.mrn,
                'additional_info': f"Test Date: {message.test_date}. Test Time: {message.test_time}. Creatine Value: {message.creatine_value}"
            }
        
        # Append the data to the CSV file
        with open('message_log.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writerow(row_data)

    def instantiate_all_past_messages_from_log(self, message_log_filepath):
        """
        Reads message_log.csv, sorts messages chronologically, and creates message object instances.
        """
        # Check if the CSV file exists
        if not os.path.exists(message_log_filepath):
            # Create an empty CSV file
            with open(message_log_filepath, 'w', newline=''):
                pass
        else:
            # Read the history.csv file to populate the creatine_results_history dictionary
            df = pd.read_csv(message_log_filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            sorted_df = df.sort_values(by='timestamp')
            
            for _, row in sorted_df.iterrows():
                if row['type'] == 'PatientAdmission':
                    # Assuming additional_info contains comma-separated data
                    info_parts = row['additional_info'].split('. ')
                    name = info_parts[0].split(': ')[1]
                    dob = info_parts[1].split(': ')[1]
                    sex = info_parts[2].split(': ')[1]
                    self.add_admitted_patient_to_current_patients(PatientAdmissionMessage(row['mrn'], 
                                            name, dob, 
                                            sex, 
                                            storage_manager))
                    
                elif row['type'] == 'PatientDischarge':
                    self.storage_manager.add_test_result_to_current_patients(PatientDischargeMessage(row['mrn'], 
                                            storage_manager))
                    
                elif row['type'] == 'TestResult':
                    info_parts = row['additional_info'].split('. ')
                    test_date = info_parts[0].split(': ')[1]
                    test_time = info_parts[1].split(': ')[1]
                    creatine_value = float(info_parts[2].split(': ')[1])
                    self.remove_patient_from_current_patients(TestResultMessage(row['mrn'], 
                                    test_date, 
                                    test_time, 
                                    creatine_value, 
                                    storage_manager, 
                                    trigger_aki_prediction=False))

if __name__ == "__main__":
    storage_manager = StorageManager()
    storage_manager.initialise_database()
    
    print(storage_manager.creatine_results_history)
    
    # admission_msg = PatientAdmissionMessage(mrn='822825', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    # storage_manager.add_admitted_patient_to_dict(admission_msg)
    # print(storage_manager.current_patients)
    
    # test_result_msg = TestResultMessage(mrn='822825', test_date='2021-01-01', test_time='08:00', creatine_value=1.2)
    # storage_manager.add_test_result_to_database(test_result_msg)
    
    # discharge_msg = PatientDischargeMessage(mrn='822825')
    # storage_manager.remove_patient_from_dict(discharge_msg.mrn)
    # print(storage_manager.current_patients)
    
    # admission_msg = PatientAdmissionMessage(mrn='822825', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    # storage_manager.add_admitted_patient_to_dict(admission_msg)
    # print(storage_manager.current_patients)

    
    