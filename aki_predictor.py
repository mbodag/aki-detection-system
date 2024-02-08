#!/usr/bin/env python3

import argparse
import csv
import datetime
import pickle
import numpy as np


class AKIPredictor:
    """A class to predict Acute Kidney Injury (AKI) based on patient data."""

    def __init__(self, storage_manager):
        """
        Initializes the AKIPredictor instance.

        Parameters:
        storage_manager: An instance responsible for managing patient data storage.
        """
        self.storage_manager = storage_manager
        self.model = self.load_model()

    def load_model(self):
        """Loads the predictive model from a file.

        Returns:
        The loaded predictive model.
        """
        with open("/model/finalized_model.pkl", "rb") as model_file:
            return pickle.load(model_file)

    @staticmethod
    def determine_age(date_of_birth):
        """
        Determine the age of the patient.

        Parameters:
        date_of_birth (str): The date of birth of the patient in the format YYYY-MM-DD.

        Returns:
        int: The age of the patient.
        """
        today = datetime.date.today()
        dob = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def predict_aki(self, mrn):
        """
        Predicts whether a patient is at risk of AKI based on their medical record number (MRN).

        Parameters:
        mrn (str): The medical record number of the patient.

        Returns:
        int: 0 if no AKI is predicted, 1 if AKI is predicted.
        """
        # Access the data from current_patients dictionary
        patient_data = self.storage_manager.current_patients.get(mrn)

        if patient_data is None:
            raise ValueError(f"Patient with MRN {mrn} not found in current_patients dictionary.")

        sex = 0 if patient_data['sex'] == 'm' else 1
        age = self.determine_age(patient_data['date_of_birth'])

        creatinine_results = patient_data['creatinine_results']

        # Number of creatinine results to use in the model
        X_train_creatinine_columns = 9

        # Adjust creatinine results to match model input requirements
        if len(creatinine_results) > X_train_creatinine_columns:
            recent_results = creatinine_results[-X_train_creatinine_columns:]
        else:
            while len(creatinine_results) < X_train_creatinine_columns + 2:
                creatinine_results.append(creatinine_results[-1])
            recent_results = creatinine_results

        input_features = [sex, age] + recent_results

        # Predict AKI and return the prediction
        return self.model.predict(np.array(input_features, dtype=np.float64).reshape(1, -1))[0]
