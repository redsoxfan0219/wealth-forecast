class Income():
    
    def __init__(self,
                 base_salary:int,
                 paycheck_non401k_pre_tax_deductions: float,
                 paycheck_schedule: str,
                 pre_tax_401k_contribution_rate: float,
                 ):
        
        self.base_salary = base_salary
        self.paycheck_non401k_pre_tax_deductions = paycheck_non401k_pre_tax_deductions
        self.paycheck_schedule = paycheck_schedule
        self.pre_tax_401k_contribution_rate = pre_tax_401k_contribution_rate
        self.paycheck_non401k_pre_tax_deductions = paycheck_non401k_pre_tax_deductions
        self.number_of_paychecks = self.derive_number_of_paychecks()
        self.paycheck_gross = self.derive_paycheck_gross()
        self.paycheck_taxable_income = self.derive_paycheck_taxable_income()
    
    def derive_number_of_paychecks(self):
        
        if "bi" in self.paycheck_schedule.lower():
            number_of_paychecks = 26
        elif "week" in self.paycheck_schedule.lower():
            number_of_paychecks = 52
        elif "month" in self.paycheck_schedule.lower():
            number_of_paychecks = 12
            
        return number_of_paychecks
                    
    def derive_paycheck_gross(self):
        
        paycheck_gross = self.base_salary / self.derive_number_of_paychecks()
        return paycheck_gross
    
    def derive_paycheck_taxable_income(self):
    
        return self.paycheck_gross - self.paycheck_non401k_pre_tax_deductions - (self.paycheck_gross * self.pre_tax_401k_contribution_rate)
    
    def derive_paycheck_take_home(self):
        
        return self.paycheck_taxable_income * (1 - marginal_tax_rate)