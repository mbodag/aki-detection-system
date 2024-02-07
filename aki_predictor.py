#!/usr/bin/env python3

import argparse
import csv
import datetime
import pickle
import numpy as np

def aki_predictor(patient_dict,MRN):

    # Load the model
    model = pickle.load(open("/model/finalized_model.pkl", "rb"))

    # Access the data dictionary indexed by MRN
    data = patient_dict[MRN]

    if data is None:
        print("MRN not found in the current_patients dictionary.")
        return
    
    # Unpack data
    sex = data['sex']
    if sex == 'm':
        sex = 0
    elif sex == 'f':
        sex = 1
    age = data['age']
    results = data['creatinine']

    # Remove dates and empty strings from results
    results = [item for item in results if not is_date(item) and item != ""]

    # Number of creatinine results to use in the model
    X_train_creatinine_columns = 9 # number of columns in X_train excluding age and sex
    
    # Truncate rows with more than 11 columns and keep most recent test results
    if len(results) > X_train_creatinine_columns:
        recent_results = results[-X_train_creatinine_columns:]

        results = []
        results.append(sex)
        results.append(age)
        results.extend(recent_results)
    
    # Impute rows with empty values to match the length of the longest row
    while len(results) < X_train_creatinine_columns+2:
        results.append(results[-1]) # fill out shorter rows with the lastest value
        
    # Predict AKI and write to aki.csv
    return model.predict(np.array(results, dtype=np.float64).reshape(1, -1))[0] # 0 for no AKI, 1 for AKI


def is_date(item):
    try:
        datetime.datetime.strptime(item, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False