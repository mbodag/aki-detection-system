class PatientAdmissionMessage():
    """
    Handles patient admission messages.
    """
    def __init__(self, mrn, name, date_of_birth, sex):
        self.mrn = mrn
        self.name = name
        self.date_of_birth = date_of_birth
        self.sex = sex
       

class PatientDischargeMessage():
    """
    Handles patient discharge messages.
    """
    def __init__(self, mrn):
        self.mrn = mrn
   
class TestResultMessage():
    """
    Handles test result messages.
    """
    def __init__(self, mrn, test_date, test_time, creatine_value, trigger_aki_prediction=True):
        self.mrn = mrn
        self.test_date = test_date
        self.test_time = test_time
        self.creatine_value = creatine_value
        
 
# Example usage
if __name__ == "__main__":
    admission_msg = PatientAdmissionMessage(mrn='123', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    discharge_msg = PatientDischargeMessage(mrn='123')
    test_result_msg = TestResultMessage(mrn='123', test_date='2021-01-01', test_time='08:00', creatine_value=1.2)