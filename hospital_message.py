class PatientAdmissionMessage():
    """
    Handles patient admission messages.
    """
    def __init__(self, mrn: str, name: str, date_of_birth: str, sex: str):
        self.mrn = mrn
        self.name = name
        self.date_of_birth = date_of_birth
        self.sex = sex
       
class PatientDischargeMessage():
    """
    Handles patient discharge messages.
    """
    def __init__(self, mrn: str):
        self.mrn = mrn
   
class TestResultMessage():
    """
    Handles test result messages.
    """
    def __init__(self, mrn: str, test_date: str, test_time: str, creatine_value: float, trigger_aki_prediction: bool =True):
        self.mrn = mrn
        self.test_date = test_date
        self.test_time = test_time
        self.creatine_value = creatine_value
        self.timestamp = test_date[0:4] + test_date[5:7] + test_date[8:10] + test_time[0:2] + test_time[3:5]
 
# Example usage
if __name__ == "__main__":
    admission_msg = PatientAdmissionMessage(mrn='123', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    discharge_msg = PatientDischargeMessage(mrn='123')
    test_result_msg = TestResultMessage(mrn='123', test_date='2021-01-01', test_time='08:00', creatine_value=1.2)