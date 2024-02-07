# alert_manager.py

import requests
from config import ALERT_SERVICE_ENDPOINT

class AlertManager:
    """
    AlertManager handles the communication with the hospital's alerting system.
    """

    @staticmethod
    def send_alert(patient_mrn):
        """
        Send an alert for the specified patient MRN.

        Parameters:
        patient_mrn (str): The medical record number of the patient.
        """
        try:
            alert_data = patient_mrn
            headers = {
                "Content-Type": "text/plain"
            }
            response = requests.post("/page", data=alert_data, headers=headers)
            response.raise_for_status()
            print(f"Alert sent for patient MRN: {patient_mrn}")
        except requests.RequestException as e:
            print(f"Failed to send alert: {e}")

# Example usage:
# AlertManager.send_alert('12345678')
