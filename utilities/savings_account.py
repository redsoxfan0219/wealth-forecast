class SavingsAccount:
    
    def __init__(self, 
                 current_account_value: float,
                 current_account_interest_rate: float, 
                 income_1: Income,
                 income_2: Income = None,
                 income1_base_monthly_contribution: float = 0,
                 income1_base_monthly_contribution_percent: float = 0,
                 income1_base_monthly_deduction: float = 0,
                 income1_base_monthly_deduction_percent: float = 0,
                 income1_current_month_contribution: float = 0,
                 income1_current_month_deduction: float = 0,
                 income2_base_monthly_contribution: float = 0,
                 income2_base_monthly_contribution_percent: float = 0,
                 income2_base_monthly_deduction: float = 0,
                 income2_base_monthly_deduction_percent: float = 0,
                 income2_current_month_contribution: float = 0,
                 income2_current_month_deduction: float = 0): 
        
        self.current_account_value = current_account_value
        self.current_account_interest_rate = current_account_interest_rate
        self.income1 = income_1
        self.income2 = income_2
        self.income1_base_monthly_contribution = self.set_income_base1_contribution(income1_base_monthly_contribution, income1_base_monthly_contribution_percent)
        self.income1_base_monthly_deduction_percent = income1_base_monthly_deduction_percent
        self.income1_base_monthly_deduction = income1_base_monthly_deduction
        self.income1_current_month_contribution = income1_current_month_contribution
        self.income1_current_month_deduction = income1_current_month_deduction
        self.income2_base_monthly_contribution = self.set_income_base2_contribution(income2_base_monthly_contribution, income2_base_monthly_contribution_percent)
        self.income2_base_monthly_deduction_percent = income2_base_monthly_deduction_percent
        self.income2_base_monthly_deduction = income2_base_monthly_deduction
        self.income2_current_month_contribution = income2_current_month_contribution
        self.income2_current_month_deduction = income2_current_month_deduction
        self.current_month_net_contribution = self.calculate_current_month_net_contribution()

    def set_income_base1_contribution(self, income1_base_monthly_contribution, income1_base_monthly_contribution_percent):
        
        if income1_base_monthly_contribution_percent == 0:
            return income1_base_monthly_contribution
        else:
            return self.income1.derive_paycheck_taxable_income() * income1_base_monthly_contribution_percent
        
    def set_income_base2_contribution(self, income2_base_monthly_contribution, income2_base_monthly_contribution_percent):
        
        if income2_base_monthly_contribution_percent == 0:
            return income2_base_monthly_contribution
        else:
            return self.income2.derive_paycheck_taxable_income() * income2_base_monthly_contribution_percent

    def calculate_current_month_net_contribution(self):
    # Determine Income 1 Deduction for This Month
        if self.income1_current_month_contribution != 0:
            income1_contribution = self.income1_current_month_contribution
        else:
            income1_contribution = self.income1_base_monthly_contribution
        
        # Determine Income 2 Contribution for This Month
        if self.income2_current_month_contribution != 0:
            income2_contribution = self.self.income2_current_month_contribution
        else:
            income2_contribution = self.income2_base_monthly_contribution 
            
         # Determine Income 1 Deduction for This Month
        if self.income1_current_month_deduction != 0:
            income1_deduction = self.income1_current_month_deduction
        else:
            income1_deduction = self.income1_base_monthly_deduction
        
        # Determine Income 2 deduction for This Month
        if self.income2_current_month_deduction != 0:
            income2_deduction = self.income2_current_month_deduction
        else:
            income2_deduction = self.income2_base_monthly_deduction
        
        month_net_contribution = (income1_contribution + income2_contribution) - (income1_deduction + income2_deduction)
        
        return month_net_contribution