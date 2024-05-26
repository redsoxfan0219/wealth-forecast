import csv
import pandas as pd
from datetime import datetime, timedelta
import os

################################
# Enter User Monthly Values Here
################################

# Forecast Details
forecast_length = 60 # number of months forward

# Income Details
ben_salary = 165000 # Annualized Dollar Value
nadia_salary = 90000 # Annualized Dollar Value
ben_pay_schedule = 'biweekly' # weekly, biweekly, or monthly
nadia_pay_schedule = 'weekly' # weekly, biweekly, or monthly

# Mortgage Details
mortgage_origination_date = "08-2020" # MM-YYYY
mortgage_length = 30 # Number of Years
mortgage_interest_rate = 0.0299 # Interest rate should be proportion of 1
mortgage_initial_upb = 320100
mortgage_current_upb = 289500
mortgage_prepayment_this_month=0
current_monthly_escrow = 697.33
monthly_pmi = 95.00
recorded_home_valuation = 345000
mortgage_one_time_prepayment = 0
recurring_mortgage_prepayment = 0

# Other Loan Details
student_loan_avg_interest_rate = .061
student_loan_initial_upb = 61000
student_loan_current_upb = 50500
student_loan_term = 10 # Number of Years

student_loan_prepayment_this_month= 0
student_loan_recurring_prepayment = 1000
car_loan_one_time_prepayment = 0
car_loan_recurring_prepayment = 0

# Investment Details
avg_equity_return = .08 # Represent return as proportion of 1 - 8% = .08
ben_401k_pretax_contribution_rate = 0.135
nadia_401k_pretax_contribution_rate = 0

# Saving Account Details

# Tax Details
marginal_tax_rate = 0.24

############################################
## Setting Up Incomes, Debts, Investments ##
############################################

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

class Loan:
    def __init__(self, 
                initial_upb: int,
                interest_rate: float, 
                term: int, 
                origination_date=None, 
                current_upb: int = None,
                one_time_prepayment=0,
                recurring_prepayment=0):
        if origination_date is None:
            origination_date = datetime.now()
        elif isinstance(origination_date, str) and len(origination_date) == 7:
            try:
                origination_date = datetime.strptime(origination_date, '%m-%Y')
            except ValueError:
                raise ValueError("Invalid origination date format. Please provide date in MM-YYYY format.")
        self.origination_date = origination_date
        self.initial_upb = initial_upb
        self.interest_rate = interest_rate
        self.term = term
        self.current_upb = current_upb if current_upb is not None else initial_upb
        self.one_time_prepayment = one_time_prepayment
        self.recurring_prepayment = recurring_prepayment
    
class Mortgage(Loan):
    
    def __init__(self, 
                initial_upb: int,
                interest_rate: float, 
                term: int, 
                monthly_escrow: float,
                origination_date: str, 
                recorded_home_valuation = recorded_home_valuation,
                current_upb: int = None,
                recurring_prepayment: int = 0,
                one_time_prepayment: int = 0
                ):
        super().__init__(initial_upb=initial_upb, 
                         interest_rate=interest_rate,
                         term=term,
                         origination_date=origination_date,
                         current_upb=current_upb,
                         one_time_prepayment=mortgage_one_time_prepayment,
                         recurring_prepayment=recurring_mortgage_prepayment
                        )
        self.origination_date = self.convert_date_to_dt_obj(origination_date)
        self.monthly_escrow = monthly_escrow
        self.recorded_valuation = recorded_home_valuation
        self.pmi = self.calculate_monthly_pmi_payment()
        self.amortization_schedule = self.calculate_amortization_schedule()
        
    def convert_date_to_dt_obj(self, date: str):
        
        return datetime.strptime(date,  "%m-%Y")
        
    def convert_dt_obj_to_string(self, dt_obj: datetime):
        
        return datetime.strftime("%m-%Y")
        
    def calculate_amortization_schedule(self, prepayment_this_month: int = 0):
        # Create Calculations for initial values
        initial_upb_float = float(self.initial_upb)
        monthly_interest_rate = self.interest_rate / 12
        monthly_interest = monthly_interest_rate * initial_upb_float
        base_principal_and_interest = (initial_upb_float * monthly_interest_rate) / (1- (1 + monthly_interest_rate) ** -self.term)
        monthly_payment = base_principal_and_interest + self.pmi + self.monthly_escrow
        principal_payment = monthly_payment - monthly_interest - self.pmi - self.monthly_escrow
        remaining_balance = initial_upb_float - principal_payment
        
        # Set up Dataframe with first row
        amortization_schedule = pd.DataFrame(columns=['Month', 'Payment', 'Interest', 'Principal', 'UPB'])
        amortization_schedule.loc[0] = [self.origination_date.strftime("%m-%Y"),
                                        monthly_payment, 
                                        monthly_interest, 
                                        principal_payment, 
                                        remaining_balance]
        
        self.current_upb = remaining_balance
        
        next_month_date = self.origination_date # Bump this date for each iteration of loop
        # Populate t+1...t+n table rows
        for month in range(1, int(self.term) + 1):
            # Calculations for t+1...t+n table rows
            monthly_interest = monthly_interest_rate * self.current_upb 
            principal_payment = base_principal_and_interest - monthly_interest
            monthly_payment = base_principal_and_interest + self.pmi + self.monthly_escrow
            remaining_balance = self.current_upb - principal_payment
            
            # Add to existing dataframe
            amortization_schedule.loc[month] = [next_month_date.strftime("%m-%Y"),
                                            monthly_payment, 
                                            monthly_interest, 
                                            principal_payment, 
                                            remaining_balance]
            # Update Current UPB
            self.current_upb = remaining_balance
            
            # Increment the next month date for the next iteration
            next_month_date += pd.DateOffset(months=1)
        
        amortization_schedule = amortization_schedule.round(2) ## Round pennies
        amortization_schedule.to_csv("mortgage_amortization.csv")
        return amortization_schedule
    
    def calculate_monthly_pmi_payment(self):
        if self.current_upb / self.recorded_valuation < 0.80:
            pmi = monthly_pmi
        else:
            pmi = 0
        return pmi

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


################################
## Primary Forecast function ##
################################

def monthly_forecasting(income_1: Income, 
                        income_2: Income,
                        wealth_df: pd.DataFrame):
    
    mortgage = Mortgage(
            origination_date=mortgage_origination_date, 
            initial_upb=mortgage_initial_upb, 
            interest_rate=mortgage_interest_rate, 
            term=(mortgage_length*12), 
            current_upb=mortgage_current_upb,
            monthly_escrow=current_monthly_escrow,
            recurring_prepayment=recurring_mortgage_prepayment,
            one_time_prepayment=mortgage_one_time_prepayment)
    
    student_loans = Loan(
            origination_date="08-2020",
            interest_rate=student_loan_avg_interest_rate,
            initial_upb=student_loan_initial_upb, 
            term=(student_loan_term*12), # Convert to Months 
            current_upb=student_loan_current_upb,
            recurring_prepayment=student_loan_recurring_prepayment,
            one_time_prepayment=student_loan_prepayment_this_month)
    
    car_loans = Loan(
            origination_date='10-2023', 
            initial_upb=14100,
            interest_rate=0.0499, 
            term=36, 
            current_upb=12700,
            one_time_prepayment=car_loan_one_time_prepayment,
            recurring_prepayment=car_loan_recurring_prepayment)
    
    marcus_emergency_savings_account = SavingsAccount(
            income_1=income_1,
            current_account_value=19000, 
            income1_base_monthly_contribution=0, 
            income1_base_monthly_deduction=0, 
            current_account_interest_rate=0.045)
    
    marcus_emergency_vacation_account = SavingsAccount(
            current_account_value=1500, 
            income_1=income_1,
            income1_base_monthly_contribution=400, 
            income1_base_monthly_deduction=0, 
            current_account_interest_rate=0.045)
    
    marcus_cd = SavingsAccount(
            income_1=income_1,
            current_account_value=25100, 
            income1_base_monthly_contribution=0,
            income1_base_monthly_deduction=0,
            current_account_interest_rate=0.055)
    
    nationwide_401k = FourZeroOneKay(income=income_1,
                                         existing_investment=75000,
                                         base_monthly_contribution_percent=0.00,
                                         employer_match_percent=0.00)
    fanniemae_401k = FourZeroOneKay(income=income_1, 
                                    existing_investment=4500, 
                                    base_monthly_contribution_percent=0.135,
                                    employer_match_percent=.08)
    ohio_state_403b = FourZeroOneKay(income=income_2,
                                     existing_investment=55000,
                                     base_monthly_contribution_percent=0.00,
                                     employer_match_percent=0.00)
    ohio_state_rollover = RothIRA(income=income_1, existing_investment=19200)
    brokerage_account = EquityInvestment(6700, average_return=avg_equity_return)
    
    projected_wealth = wealth_df.copy()
    
    ## Calculate t+1 forecast
    
    # Calculate Mortgage Info
    next_month_date = (datetime.now() + pd.DateOffset(months=1)).strftime("%m-%Y")
    if next_month_date in mortgage.amortization_schedule['Month'].values:
        next_month_index = mortgage.amortization_schedule.index[mortgage.amortization_schedule['Month'] == next_month_date][0]
        next_month_principal = mortgage.amortization_schedule.at[next_month_index, 'Principal']
        next_month_interest = mortgage.amortization_schedule.at[next_month_index, 'Interest']
        mortgage_payment = mortgage.monthly_escrow + mortgage.one_time_prepayment + next_month_interest + next_month_principal
    else:
        print(f"No data found for {next_month_date}. Skipping calculations for this month.")
    
    # Calculate total payments
    next_month_mortgage_interest_payment = mortgage.amortization_schedule.at[next_month_index, 'Interest']
    
    ## Assume if making a one time prepayment this overrides (not adds to) normal prepayment
    if mortgage.one_time_prepayment > 0:
        mortgage_payment = mortgage.monthly_escrow + next_month_mortgage_interest_payment + mortgage.amortization_schedule.at[next_month_index, 'Principal'] + mortgage.one_time_prepayment
    else:
        mortgage_payment = mortgage.monthly_escrow + next_month_mortgage_interest_payment + mortgage.amortization_schedule.at[next_month_index, 'Principal'] + mortgage.recurring_prepayment
        
    ## Student Loans - Same logic as above
    
    if student_loans.one_time_prepayment > 0:
        student_loan_payment =  600 + student_loans.one_time_prepayment
    else:
        student_loan_payment =  600 + student_loans.recurring_prepayment
      
    ## Car Loan - Same Logic as Above  
    if car_loans.one_time_prepayment > 0:
        car_loan_payment =  436 + car_loans.one_time_prepayment
    else:
        car_loan_payment =  436 + car_loans.recurring_prepayment
    
    # Calculations for Investments    
    emergency_savings_delta = projected_wealth.at[0, 'Marcus_Emergency_Savings'] * (1 + marcus_emergency_savings_account.current_account_interest_rate / 12) - projected_wealth.at[0, 'Marcus_Emergency_Savings']
    vacation_savings_delta = projected_wealth.at[0, 'Marcus_Vacation_Savings'] * (1 + marcus_emergency_vacation_account.current_account_interest_rate / 12) - projected_wealth.at[0, 'Marcus_Vacation_Savings']
    marcus_cd_delta = projected_wealth.at[0, 'Marcus_CD'] * (1 + marcus_cd.current_account_interest_rate / 12) - projected_wealth.at[0, 'Marcus_CD']
    nationwide_delta = projected_wealth.at[0, 'Nationwide_401k_Value'] * (1 + nationwide_401k.average_return / 12) - projected_wealth.at[0, 'Nationwide_401k_Value']
    fannie_delta = projected_wealth.at[0, 'Fannie_Mae_401k_Value'] * (1 + fanniemae_401k.average_return / 12) - projected_wealth.at[0, 'Fannie_Mae_401k_Value']
    rollover_delta = projected_wealth.at[0, 'Ben_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12) - projected_wealth.at[0, 'Ben_Rollover_IRA_Value']
    ohio_state_delta = projected_wealth.at[0, 'Nadia_OhioState_403b'] * (1 + ohio_state_403b.average_return / 12) - projected_wealth.at[0, 'Nadia_OhioState_403b']
    brokerage_delta = projected_wealth.at[0, 'Brokerage_Account'] * (1 + brokerage_account.average_return / 12) - projected_wealth.at[0, 'Brokerage_Account']        

    # Update the current wealth data with the projections for this month
    projected_wealth.loc[1] = [next_month_date,
                                projected_wealth.at[0, 'Total_Wealth'] + next_month_principal + student_loan_payment + student_loan_prepayment_this_month + car_loan_payment + emergency_savings_delta + vacation_savings_delta + marcus_cd_delta + nationwide_delta + fannie_delta + rollover_delta + ohio_state_delta + brokerage_delta,
                                projected_wealth.at[0, 'Mortgage_UPB'] - mortgage.amortization_schedule.at[next_month_index, 'Principal'],
                                projected_wealth.at[0, 'Student_Loan_UPB'] - student_loan_payment,
                                projected_wealth.at[0, 'Car_Loan'] - car_loan_payment,
                                projected_wealth.at[0, 'Marcus_Emergency_Savings'] * (1 + marcus_emergency_savings_account.current_account_interest_rate / 12) + marcus_emergency_savings_account.calculate_current_month_net_contribution(),
                                projected_wealth.at[0, 'Marcus_Vacation_Savings'] * (1 + marcus_emergency_vacation_account.current_account_interest_rate / 12) + marcus_emergency_vacation_account.calculate_current_month_net_contribution(),
                                projected_wealth.at[0, 'Marcus_CD'] * (1 + marcus_cd.current_account_interest_rate / 12),
                                projected_wealth.at[0, 'Nationwide_401k_Value'] * (1 + nationwide_401k.average_return / 12) + nationwide_401k.calculate_monthly_total_contribution(),
                                projected_wealth.at[0, 'Fannie_Mae_401k_Value'] * (1 + fanniemae_401k.average_return / 12) + fanniemae_401k.calculate_monthly_total_contribution(),
                                projected_wealth.at[0, 'Ben_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12),
                                projected_wealth.at[0, 'Nadia_OhioState_403b'] * (1 + ohio_state_403b.average_return / 12),
                                projected_wealth.at[0, 'Brokerage_Account'] * (1 + brokerage_account.average_return / 12)]
    
    ## Calculate t+2 forecast 
    
    for i in range(2, forecast_length):
        # Calculate next month's date
        next_month_date = (datetime.now() + pd.DateOffset(months=i)).strftime("%m-%Y")
        
        # Calculate Mortgage Info
        if next_month_date in mortgage.amortization_schedule['Month'].values:
            next_month_index = mortgage.amortization_schedule.index[mortgage.amortization_schedule['Month'] == next_month_date][0]
            next_month_principal = mortgage.amortization_schedule.at[next_month_index, 'Principal']
            next_month_interest = mortgage.amortization_schedule.at[next_month_index, 'Interest']
            mortgage_payment = mortgage.monthly_escrow + mortgage.recurring_prepayment + next_month_interest + next_month_principal + mortgage.recurring_prepayment
        else:
            print(f"No data found for {next_month_date}. Skipping calculations for this month.")
            continue
        
        # Calculate total payments
        next_month_mortgage_interest_payment = mortgage.amortization_schedule.at[next_month_index, 'Interest']
        mortgage_payment = mortgage.monthly_escrow + mortgage.recurring_prepayment + next_month_mortgage_interest_payment + mortgage.amortization_schedule.at[next_month_index, 'Principal']
        student_loan_payment = 600 + student_loans.recurring_prepayment
        car_loan_payment = 438 + car_loans.recurring_prepayment
        total_401k_contributions = nationwide_401k.calculate_monthly_total_contribution() + fanniemae_401k.calculate_monthly_total_contribution()
        
        emergency_savings_delta = projected_wealth.at[i - 1, 'Marcus_Emergency_Savings'] * (1 + marcus_emergency_savings_account.current_account_interest_rate / 12) - projected_wealth.at[i - 1, 'Marcus_Emergency_Savings']
        vacation_savings_delta = projected_wealth.at[i - 1, 'Marcus_Vacation_Savings'] * (1 + marcus_emergency_vacation_account.current_account_interest_rate / 12) - projected_wealth.at[i - 1, 'Marcus_Vacation_Savings']
        marcus_cd_delta = projected_wealth.at[i - 1, 'Marcus_CD'] * (1 + marcus_cd.current_account_interest_rate / 12) - projected_wealth.at[i - 1, 'Marcus_CD']
        nationwide_delta = projected_wealth.at[i - 1, 'Nationwide_401k_Value'] * (1 + nationwide_401k.average_return / 12) - projected_wealth.at[i - 1, 'Nationwide_401k_Value']
        fannie_delta = projected_wealth.at[i - 1, 'Fannie_Mae_401k_Value'] * (1 + fanniemae_401k.average_return / 12) - projected_wealth.at[i - 1, 'Fannie_Mae_401k_Value']
        rollover_delta = projected_wealth.at[i - 1, 'Ben_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12) - projected_wealth.at[i - 1, 'Ben_Rollover_IRA_Value']
        ohio_state_delta = projected_wealth.at[i - 1, 'Nadia_OhioState_403b'] * (1 + ohio_state_403b.average_return / 12) - projected_wealth.at[i - 1, 'Nadia_OhioState_403b']
        brokerage_delta = projected_wealth.at[i - 1, 'Brokerage_Account'] * (1 + brokerage_account.average_return / 12) - projected_wealth.at[i - 1, 'Brokerage_Account']
        
        if projected_wealth.at[i - 1, 'Mortgage_UPB'] - mortgage_payment < 0:
            # If UPB is negative, redirect the payment to emergency savings
            fannie_delta += mortgage_payment
            # Set mortgage UPB and payment to 0
            projected_wealth['Mortgage_UPB'].loc[i]= 0
            mortgage_payment = 0

        if projected_wealth.at[i - 1, 'Student_Loan_UPB'] - student_loan_payment < 0:
            # If UPB is negative, redirect the payment in the following order:
            ## Car Loan then Investment Account
            if projected_wealth.at[i - 1, 'Car_Loan'] - student_loan_payment > 0:
                car_loan_payment += student_loan_payment
            else:    
                brokerage_delta += student_loan_payment + student_loan_prepayment_this_month
                # Set loan UPB and payments to 0 for remaining months
                projected_wealth['Student_Loan_UPB'].loc[i] = 0
                student_loan_payment = 0
            

        if projected_wealth.at[i - 1, 'Car_Loan'] - car_loan_payment < 0:
            # If UPB is negative, redirect the payment in the following order:
            ## Car Loan then Investment Account
            if projected_wealth.at[i - 1, 'Car_Loan'] - student_loan_payment > 0:
                student_loan_payment += car_loan_payment
            else:    
                brokerage_delta += student_loan_payment + student_loan_recurring_prepayment
                # Set car loan UPB and payment to 0
                projected_wealth.at[i, 'Car_Loan'] = 0
                car_loan_payment = 0
            

        # Update the current wealth data with the projections for this month
        projected_wealth.loc[i] = [next_month_date,
                                    projected_wealth.at[i - 1, 'Total_Wealth'] + next_month_principal + student_loan_payment + student_loans.recurring_prepayment + car_loan_payment + emergency_savings_delta + vacation_savings_delta + marcus_cd_delta + nationwide_delta + fannie_delta + rollover_delta + ohio_state_delta + brokerage_delta,
                                    projected_wealth.at[i - 1, 'Mortgage_UPB'] - mortgage.amortization_schedule.at[next_month_index, 'Principal'],
                                    projected_wealth.at[i - 1, 'Student_Loan_UPB'] - student_loan_payment,
                                    projected_wealth.at[i - 1, 'Car_Loan'] - car_loan_payment,
                                    projected_wealth.at[i - 1, 'Marcus_Emergency_Savings'] * (1 + marcus_emergency_savings_account.current_account_interest_rate / 12) + marcus_emergency_savings_account.calculate_current_month_net_contribution(),
                                    projected_wealth.at[i - 1, 'Marcus_Vacation_Savings'] * (1 + marcus_emergency_vacation_account.current_account_interest_rate / 12) + marcus_emergency_vacation_account.calculate_current_month_net_contribution(),
                                    projected_wealth.at[i - 1, 'Marcus_CD'] * (1 + marcus_cd.current_account_interest_rate / 12),
                                    projected_wealth.at[i - 1, 'Nationwide_401k_Value'] * (1 + nationwide_401k.average_return / 12) + nationwide_401k.calculate_monthly_total_contribution(),
                                    projected_wealth.at[i - 1, 'Fannie_Mae_401k_Value'] * (1 + fanniemae_401k.average_return / 12) + fanniemae_401k.calculate_monthly_total_contribution(),
                                    projected_wealth.at[i - 1, 'Ben_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12),
                                    projected_wealth.at[i - 1, 'Nadia_OhioState_403b'] * (1 + ohio_state_403b.average_return / 12),
                                    projected_wealth.at[i - 1, 'Brokerage_Account'] * (1 + brokerage_account.average_return / 12)]
        
        if projected_wealth['Student_Loan_UPB'].loc[i] - student_loan_payment <= 0:
            projected_wealth['Student_Loan_UPB'].loc[i] = 0
        
        if projected_wealth['Mortgage_UPB'].loc[i] - mortgage_payment <= 0:
            projected_wealth['Mortgage_UPB'].loc[i] = 0
        
        if projected_wealth['Car_Loan'].loc[i] - car_loan_payment <= 0:
            projected_wealth['Car_Loan'].loc[i] = 0
        
            
    # Print the updated DataFrame
    print(mortgage.amortization_schedule)
    print(projected_wealth.round(2))
    
    projected_wealth.round(2).to_csv("new_forecast.csv")

    # Return the updated DataFrame
    return projected_wealth

def read_current_wealth(income_1: Income,
                        income_2: Income):
    # Check if "current_wealth.csv" exists in the current directory
    
    if os.path.exists("current_wealth.csv"):
        # Read data from the existing CSV file
        with open("current_wealth.csv", "r") as file:
            reader = pd.read_csv(file)
            return reader  # Add this line to return the processed data
    else:
        # Base file creation if one doesn't exist
        mortgage = Mortgage(
            origination_date="08-2020", 
            initial_upb=320100, 
            interest_rate=0.0299, 
            term=(12*30), 
            current_upb=289500,
            monthly_escrow=current_monthly_escrow,
            recorded_home_valuation=recorded_home_valuation,
            recurring_payment=0,
            one_time_prepayment=0)
        
        student_loans = Loan(
            origination_date="08-2020",
            interest_rate=6.1,
            initial_upb=61000, 
            term=120,
            current_upb=50500,
            one_time_prepayment=0,
            recurring_prepayment=0)
        
        car_loans = Loan(
            origination_date='10-2023', 
            initial_upb=14100,
            interest_rate=0.0499, 
            term=36, 
            current_upb=12700,
            recurring_prepayment=0,
            one_time_prepayment=0)
        marcus_emergency_savings_account = SavingsAccount(
            income_1=income_1,
            current_account_value=19000, 
            income1_base_monthly_contribution=0, 
            income1_base_monthly_deduction=0, 
            current_account_interest_rate=0.045)
        marcus_emergency_vacation_account = SavingsAccount(
            current_account_value=1500, 
            income_1=income_1,
            income1_base_monthly_contribution=400, 
            income1_base_monthly_deduction=0, 
            current_account_interest_rate=0.045)
        marcus_cd = SavingsAccount(
            income_1=income_1,
            current_account_value=25100, 
            income1_base_monthly_contribution=0,
            income1_base_monthly_deduction=0,
            current_account_interest_rate=0.055)
        nationwide_401k = FourZeroOneKay(income=income_1,
                                         existing_investment=75000,
                                         base_monthly_contribution_percent=0.00,
                                         employer_match_percent=0.00)
        fanniemae_401k = FourZeroOneKay(income=income_1, 
                                        existing_investment=4500,
                                        base_monthly_contribution_percent=0.135,
                                        employer_match_percent=.06)
        ohio_state_403b = FourZeroOneKay(income=income_2,
                                         existing_investment=55000,
                                         base_monthly_contribution_percent=0.00,
                                         employer_match_percent=0.00)
        ohio_state_rollover = RothIRA(income=income_1, 
                                      existing_investment=18000,
                                      base_monthly_contribution_percent=0.00,
                                      employer_match_percent=0.00)
        brokerage_account = EquityInvestment(6700, average_return=avg_equity_return)
        
        total_wealth_sum = (
            marcus_emergency_savings_account.current_account_value +
            marcus_emergency_vacation_account.current_account_value +
            marcus_cd.current_account_value +
            nationwide_401k.existing_investment +
            fanniemae_401k.existing_investment +
            ohio_state_rollover.existing_investment +
            ohio_state_403b.existing_investment +
            brokerage_account.existing_investment
        ) - (
            mortgage.current_upb +
            student_loans.current_upb +
            car_loans.current_upb
        )


        wealth_data = {
        'Date': [f'{datetime.now().month}-{datetime.now().year}'],
        'Total_Wealth': [total_wealth_sum],
        'Mortgage_UPB': [mortgage.current_upb],
        'Student_Loan_UPB': [student_loans.current_upb],
        'Car_Loan': [car_loans.current_upb],
        'Marcus_Emergency_Savings': [marcus_emergency_savings_account.current_account_value],
        'Marcus_Vacation_Savings': [marcus_emergency_vacation_account.current_account_value],
        'Marcus_CD': [marcus_cd.current_account_value],
        'Nationwide_401k_Value': [nationwide_401k.existing_investment],
        'Fannie_Mae_401k_Value': [fanniemae_401k.existing_investment],
        'Ben_Rollover_IRA_Value': [ohio_state_rollover.existing_investment],
        'Nadia_OhioState_403b': [ohio_state_403b.existing_investment],
        'Brokerage_Account': [brokerage_account.existing_investment]
        }

        wealth = pd.DataFrame(wealth_data)            
        return wealth
    
def write_current_wealth(wealth_dataframe: pd.DataFrame):
    """
    Write a Pandas DataFrame to a CSV file.
    
    Parameters:
    - df: Pandas DataFrame to write to CSV.
    - file_path: File path where the CSV file will be saved.
    """
    current_directory = os.getcwd()  # Get the current directory
    file_path = os.path.join(current_directory, "current_wealth.csv")  # Construct the file path
    wealth_dataframe.to_csv(file_path, index=False)

def main():
    
    # Set incomes
    ben_income = Income(
        base_salary=ben_salary,
        paycheck_non401k_pre_tax_deductions= 363.11,
        paycheck_schedule='biweekly',
        pre_tax_401k_contribution_rate=ben_401k_pretax_contribution_rate
    )
    
    nadia_income = Income(
        base_salary=nadia_salary,
        paycheck_non401k_pre_tax_deductions= 30.00,
        paycheck_schedule='weekly',
        pre_tax_401k_contribution_rate=nadia_401k_pretax_contribution_rate
    )
    
    # Read existing loan and investment data
    current_wealth_data = read_current_wealth(income_1=ben_income, income_2=nadia_income)

    # Update projections for the next month
    forecast = monthly_forecasting(income_1=ben_income, income_2=nadia_income, wealth_df=current_wealth_data)

    # Write updated projections to file
    write_current_wealth(current_wealth_data)

if __name__ == "__main__":
    main()
