# config.py

# The path to the CSV file where historical patient data is stored.
HISTORY_CSV_PATH = 'history.csv'
HOSPITAL_DATA_CSV_PATH = 'hospital_data.csv'

# Details for the message listener (e.g., IP and port for HL7 messages)
HL7_LISTENER_IP = '127.0.0.1'
HL7_LISTENER_PORT = 1234

# The URI for the database (SQLite in this example)
DATABASE_URI = 'sqlite:///patient_data.db'

# Add any other global configuration variables here.
