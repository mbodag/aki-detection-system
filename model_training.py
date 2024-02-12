import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle
from automated_testing import automated_test

# Read the data and name all the columns
column_names = ['age', 'sex', 'aki','creatinine_date_0', 'creatinine_result_0',
                'creatinine_date_1', 'creatinine_result_1',
                'creatinine_date_2', 'creatinine_result_2',
                'creatinine_date_3', 'creatinine_result_3',
                'creatinine_date_4', 'creatinine_result_4',
                'creatinine_date_5', 'creatinine_result_5',
                'creatinine_date_6', 'creatinine_result_6',
                'creatinine_date_7', 'creatinine_result_7',
                'creatinine_date_8', 'creatinine_result_8']

data = pd.read_csv('training.csv',header=None,skiprows = 1,names=column_names)

# Impute nan values for missing data
data = data.where(data.notna(), np.nan)

# Replace 'n' and 'y' with 0 and 1 in the target variable
data['aki'] = data['aki'].replace({'n': 0, 'y': 1})

# Replace 'm' and 'f' with 0 and 1 in the 'sex' column
data['sex'] = data['sex'].replace({'m': 0, 'f': 1})

# Filter out date columns
feature_columns = data.filter(regex='^(?!.*date).*$', axis=1)

# Separate features and target variable
y = feature_columns["aki"]
X = feature_columns.drop(["aki"], axis=1)

# Impute missing creatinine test results by carrying the last observation forward
creatinine_columns = [f'creatinine_result_{i}' for i in range(9)]
for i, row in X.iterrows():
    last_value = None
    for col in creatinine_columns:
        if pd.notna(row[col]):
            last_value = row[col]
        elif last_value is not None:
            X.at[i, col] = last_value

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Train the model
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train.values, y_train.values)

# Test that the model achieves good results
automated_test(lr_model, X_test, y_test)

# Save the model
filename = 'finalized_model.pkl'
pickle.dump(lr_model, open(filename, 'wb'))