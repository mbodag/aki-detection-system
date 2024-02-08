class PatientAdmissionMessage():
    """
    Handles patient admission messages.
    """
    def __init__(self, mrn, name, date_of_birth, sex):
        self.mrn = mrn
        self.name = name
        self.date_of_birth = date_of_birth
        self.sex = sex
        
        #self.execute_admission_actions()
        
        #print(f"Patient {self.mrn} has been admitted.")
        
    # def execute_admission_actions(self):
    #     # Appends patient to Short-Term Storage
    #     self.storage_manager.add_message_to_log_csv(self)
    #     self.storage_manager.add_admitted_patient_to_current_patients(self)        

class PatientDischargeMessage():
    """
    Handles patient discharge messages.
    """
    def __init__(self, mrn):
        self.mrn = mrn
        
        #print(f"Patient {self.mrn} has been discharged.")
        
    #     self.execute_discharge_actions()
        
    # def execute_discharge_actions(self):
    #     self.storage_manager.add_message_to_log_csv(self)
    #     self.storage_manager.update_patients_data_in_creatine_results_history(self)
    #     self.storage_manager.remove_patient_from_current_patients(self)

class TestResultMessage():
    """
    Handles test result messages.
    """
    def __init__(self, mrn, test_date, test_time, creatine_value, trigger_aki_prediction=True):
        self.mrn = mrn
        self.test_date = test_date
        self.test_time = test_time
        self.creatine_value = creatine_value
        
    #     print(f"Test result received for patient {self.mrn}: {self.creatine_value}")
        
    #     self.execute_test_result_actions(trigger_aki_prediction = trigger_aki_prediction)
        
        
    # def execute_test_result_actions(self, trigger_aki_prediction):
    #     self.storage_manager.add_message_to_log_csv(self)
    #     self.storage_manager.add_test_result_to_current_patients(self)

# Example usage
if __name__ == "__main__":
    admission_msg = PatientAdmissionMessage(mrn='123', name='John Doe', date_of_birth='1980-01-01', sex='M')   
    discharge_msg = PatientDischargeMessage(mrn='123')
    test_result_msg = TestResultMessage(mrn='123', test_date='2021-01-01', test_time='08:00', creatine_value=1.2)