import urllib
import urllib.error
import urllib.request
import os
from config import PAGER_PORT, PAGER_ADDRESS


# PAGER_ADDRESS, PAGER_PORT = os.environ['PAGER_ADDRESS'].split(":")
# PAGER_PORT = int(PAGER_PORT)

class AlertManager:
    """
    AlertManager handles the communication with the hospital's alerting system.
    """

    @staticmethod
    def send_alert(patient_mrn: str, timestamp: str):
        """
        Send an alert for the specified patient MRN.

        Parameters:
        patient_mrn (str): The medical record number of the patient.
        timestamp (str): The timestamp of the alert in the format YYYYMMDDHHMM
        """
        alert_data = bytes(patient_mrn +','+timestamp, 'utf-8')
        r = urllib.request.urlopen(f"http://{PAGER_ADDRESS}:{PAGER_PORT}/page", data=alert_data)
        