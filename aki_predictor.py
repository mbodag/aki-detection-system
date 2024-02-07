#!/usr/bin/env python3

import argparse
import csv
import datetime
import pickle
import numpy as np

class AKIPredictor:
    
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.model = self.load_model()
    
    def load_model(self):
        return pickle.load(open("/model/finalized_model.pkl", "rb"))
    
    @staticmethod
    def determine_age(date_of_birth):
        """ Determine the age of the patient.
        
        Parameters:
        date_of_birth (str): The date of birth of the patient in the format YYYY-MM-DD.
        
        Returns:
        int: The age of the patient.
        """
        today = datetime.date.today()
        date_of_birth = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d")
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    def predict_aki(self, mrn):

        # Access the data from current_patients dictionary
        patient_data = self.storage_manager.current_patients.get(mrn, None)

        if patient_data is None:
            raise ValueError(f"Patient with MRN {mrn} not found in current_patients dictionary.")
        
        sex = patient_data['sex']
        if sex == 'm':
            sex = 0
        elif sex == 'f':
            sex = 1
        age = self.determine_age(patient_data['date_of_birth'])
        
        creatinine_results = patient_data['creatinine_results']
        
        # Number of creatinine results to use in the model
        X_train_creatinine_columns = 9 # number of columns in X_train excluding age and sex
        
        # Truncate rows with more than 11 columns and keep most recent test results
        if len(creatinine_results) > X_train_creatinine_columns:
            recent_results = creatinine_results[-X_train_creatinine_columns:]
            
        else:
            # Impute rows with empty values to match the length of the longest row
            while len(creatinine_results) < X_train_creatinine_columns+2:
                creatinine_results.append(creatinine_results[-1])
            recent_results = creatinine_results
                
        input_features = []
        input_features.append(sex)
        input_features.append(age)
        input_features.extend(recent_results)
        
        # Predict AKI and write to aki.csv
        return self.model.predict(np.array(input_features, dtype=np.float64).reshape(1, -1))[0] # 0 for no AKI, 1 for AKI