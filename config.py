import os

# The path to the CSV file where historical patient data is stored.
HISTORY_CSV_PATH = '/hospital-history/history.csv'
MESSAGE_LOG_CSV_PATH = 'message_log.csv'

# These act as the header row for the MESSAGE_LOG CSV file
MESSAGE_LOG_CSV_FIELDS = ['timestamp', 'type', 'mrn', 'additional_info']

# Details for the message listener (e.g., IP and port for HL7 messages)
if os.environ.get('MLLP_ADDRESS') is None:
    MLLP_ADDRESS = "localhost"
    MLLP_PORT = 8440
else:
    MLLP_ADDRESS, MLLP_PORT = os.environ.get['MLLP_ADDRESS'].split(":")
    
if os.environ.get('PAGER_ADDRESS') is None:
    PAGER_ADDRESS = "localhost"
    PAGER_PORT = 8441
else:
    PAGER_ADDRESS, PAGER_PORT = os.environ.get['PAGER_ADDRESS'].split(":")[0]
