
class EquityInvestment:
    
    def __init__(self, 
                 existing_investment: float, 
                 average_return: avg_equity_return):
        self.existing_investment = existing_investment
        self.average_return = average_return

class FourZeroOneKay(EquityInvestment):
    
    def __init__(self, 
                 income: Income,
                 existing_investment: float, 
                 base_monthly_contribution_percent: float, 
                 employer_match_percent: float):
        super().__init__(existing_investment, average_return=avg_equity_return)
        self.income = income
        self.base_monthly_contribution_percent = base_monthly_contribution_percent
        self.employer_match_percent = employer_match_percent 
        self.base_monthly_contribution_percent = base_monthly_contribution_percent
        self.employer_match_percent = employer_match_percent
        self.employee_contribution = self.calculate_monthly_base_contribution()
        self.employer_contribution = self.calculate_employer_contribution()
        self.total_monthly_contributions = self.calculate_monthly_total_contribution()
    
    def calculate_monthly_base_contribution(self)->float:
        employee_contribution = self.income.base_salary * self.base_monthly_contribution_percent/12
        return employee_contribution
        
    def calculate_employer_contribution(self) -> float:
        employer_contribution = self.employer_match_percent * self.income.base_salary/12
        return employer_contribution

    def calculate_monthly_total_contribution(self) -> float:
        total = self.employer_contribution + self.employee_contribution
        return total
    
class RothIRA(EquityInvestment):
    
    def __init__(self, 
                 income: Income,
                 existing_investment: float, 
                 base_monthly_contribution_percent: float = 0, 
                 employer_match_percent: float = 0):
        super().__init__(existing_investment, average_return=avg_equity_return)
        self.income = income
        self.base_monthly_contribution_percent = base_monthly_contribution_percent
        self.employer_match_percent = employer_match_percent 
        self.base_monthly_contribution_percent=base_monthly_contribution_percent
        self.employer_match_percent = self.employer_match_percent
        self.employer_contribution = self.calculate_employer_contribution()
        self.post_tax_employee_contribution = self.calculate_post_tax_employee_contribution()
        self.total_monthly_contribution = self.calculate_monthly_total_contribution
            
    def calculate_post_tax_employee_contribution(self) ->float:
        return self.income.paycheck_taxable_income * (1-marginal_tax_rate)

    def calculate_employer_contribution(self) -> float:
        return self.employer_match_percent * self.income.paycheck_taxable_income

    def calculate_monthly_total_contribution(self) -> float:
        return self.post_tax_employee_contribution + self.employer_contribution