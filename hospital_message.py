class PatientAdmissionMessage():
    """
    Handles patient admission messages.
    """
    def __init__(self, mrn, name, date_of_birth, sex):
        self.mrn = mrn
        self.name = name
        self.date_of_birth = date_of_birth
        self.sex = sex
        
        print(f"Patient {self.mrn} has been admitted.")
        # add patient to short-term storage
        # check if patient is in long-term storage
        # if yes, retrieve patient data from long-term storage and sync with short-term storage
        # if not, add patient to long-term storage


class PatientDischargeMessage():
    """
    Handles patient discharge messages.
    """
    def __init__(self, mrn):
        self.mrn = mrn
        
        print(f"Patient {self.mrn} has been discharged.")
        # Validates and synchronises data across Short-Term and Long-Term Storage
        # remove patient from short-term storage


class TestResultMessage():
    """
    Handles test result messages.
    """
    def __init__(self, mrn, test_date, test_time, test_result_value):
        self.mrn = mrn
        self.test_date = test_date
        self.test_time = test_time
        self.test_result_value = test_result_value
        
        print(f"Test result received for patient {self.mrn}: {self.test_result_value}")
        # Appends laboratory results to Short-Term Storage
        # triggers the AKI prediction process
        # potentially prompts alert dispatches
        # logs results into Long-Term Storage.
        

# Example usage
if __name__ == "__main__":
    admission_msg = PatientAdmissionMessage(mrn='123', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    discharge_msg = PatientDischargeMessage(mrn='123')
    test_result_msg = TestResultMessage(mrn='123', test_date='2021-01-01', test_time='08:00', test_result_value=1.2)