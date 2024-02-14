# The path to the CSV file where historical patient data is stored.
HISTORY_CSV_PATH = 'data/history.csv'
MESSAGE_LOG_CSV_PATH = 'message_log.csv'

# These act as the header row for the MESSAGE_LOG CSV file
MESSAGE_LOG_CSV_FIELDS = ['timestamp', 'type', 'mrn', 'additional_info']


# Details for the message listener (e.g., IP and port for HL7 messages)
MLLP_PORT = 8440
PAGER_PORT = 8441

