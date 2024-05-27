import json
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path
from utilities.income import Income
from utilities.loan import Loan
from utilities.mortgage import Mortgage
from utilities.savings_account import SavingsAccount
from utilities.equities import EquityInvestment, FourZeroOneKay, RothIRA

class WealthForecast(input_data_file):
    
    def __init__(self):
        self.income_1 = None
        self.income_2 = None
    
    def add_income(self, 
                   input_income:Income):
        
        if type(self.income_1) is None:
            self.income_1 = input_income
        elif type(self.income_1) is not None and type(self.income_2) is None:
            self.income_2 = input_income
        else:
            print("Warning: input incomes already defined.")
            user_response = input("Would you like to overwrite defined income?   ")
            while user_response.lower().startswith() not in ["y", "n"]:
                user_response = input("Enter yes or no.")
            if user_response.lower().startswith("y"):
                which_to_overwrite = input("Which income would you like to overwrite, 1 or 2?   ")
                while which_to_overwrite.lstrip().rstrip() not in ["1", "2"]:
                    which_to_overwrite = input("Enter 1 or 2.   ")
                if which_to_overwrite == "1":
                    value_to_overwrite = input("Enter income to overwrite income 1:    ")
                    self.income_1 = int(value_to_overwrite)
                elif which_to_overwrite == "2":
                    value_to_overwrite = input("Enter income to overwrite income 2:    ")
                    self.income_2 = int(value_to_overwrite)
        
    def read_data(self,
                  data_file:Path):

        with open (self.input_data_file, "r") as file:
            self.input_data = json.load(file)

        # Forecast Details
        self.forecast_length = self.input_data["forecast_length"] # number of months forward

        # Income Details
        self.income_1_base_amount = self.input_data["forecast"]["income_1_base_amount"] # Annualized Dollar Value
        self.income_2_base_amount = self.input_data["income"]["income_2_base_amount"] # Annualized Dollar Value
        self.income_1_pay_schedule = self.input_data["income"]["income_1_pay_schedule"] # weekly, biweekly, or monthly
        self.income_2_pay_schedule = self.input_data["income"]["income_2_pay_schedule"] # weekly, biweekly, or monthly
        self.income_1_paycheck_non401k_pre_tax_deductions = self.input_data["income"]["income_1_paycheck_non401k_pre_tax_deductions"]
        self.income_2_paycheck_non401k_pre_tax_deductions = self.input_data["income"]["income_2_paycheck_non401k_pre_tax_deductions"]

        # Mortgage Details
        self.mortgage_origination_date = self.input_data["mortgage"]["mortgage_origination_date"] # MM-YYYY
        self.mortgage_length = self.input_data["mortgage"]["mortgage_length"] # Number of Years
        self.mortgage_interest_rate = self.input_data["mortgage"]["mortgage_interest_rate"]  # Interest rate should be proportion of 1
        self.mortgage_initial_upb = self.input_data["mortgage"]["mortgage_initial_upb"]
        self.mortgage_current_upb = self.input_data["mortgage"]["mortgage_current_upb"]
        self.mortgage_prepayment_this_month = self.input_data["mortgage"]["mortgage_prepayment_this_month"]
        self.current_monthly_escrow = self.input_data["mortgage"]["current_monthly_escrow"]
        self.monthly_pmi = self.input_data["mortgage"]["monthly_pmi"]
        self.recorded_home_valuation = self.input_data["mortgage"]["recorded_home_valuation"]
        self.mortgage_one_time_prepayment = self.input_data["mortgage"]["mortgage_one_time_prepayment"]
        self.recurring_mortgage_prepayment = self.input_data["mortgage"]["recurring_mortgage_prepayment"]

        # Other Loan Details
        self.student_loan_origination_date = self.input_data["student_loans"]["student_loan_origination_date"]
        self.student_loan_avg_interest_rate = self.input_data["student_loans"]["student_loan_avg_interest_rate"]
        self.student_loan_initial_upb = self.input_data["student_loans"]["student_loan_initial_upb"]
        self.student_loan_current_upb = self.input_data["student_loans"]["student_loan_current_upb"]
        self.student_loan_term = self.input_data["student_loans"]["student_loan_term"] # Number of Years
        self.student_loan_prepayment_this_month= self.input_data["student_loans"]["student_loan_prepayment_this_month"]
        self.student_loan_recurring_prepayment = self.input_data["student_loans"]["student_loan_recurring_prepayment"]
        
        self.car_loan_interest_rate = self.input_data["car_loan"]["car_loan_interest_rate"]
        self.car_loan_origination_date = self.input_data["car_loan"]["car_loan_origination_date"]
        self.car_loan_initial_upb = self.input_data["car_loan"]["car_loan_initial_upb"]
        self.car_loan_term_length = self.input_data["car_loan"]["car_loan_term_length"]
        self.car_loan_current_upb = self.input_data["car_loan"]["car_loan_current_upb"]
        self.car_loan_one_time_prepayment = self.input_data["car_loan"]["car_loan_one_time_prepayment"]
        self.car_loan_recurring_prepayment = self.input_data["car_loan"]["car_loan_recurring_prepayment"]

        # Investment Details
        # 401ks
        self.avg_equity_return = self.input_data["investments"]["avg_equity_return"] # Represent return as proportion of 1 - 8% = .08
        
        self.income_1_current_401k_value = self.input_data["investments"]["active_401ks"]["income_1"]["current_acct_value"]
        self.income_1_employee_contribution_rate = self.input_data["investments"]["active_401ks"]["income_1"]["employee_contribution_pct"]
        self.income_1_employer_contribution_rate = self.input_data["investments"]["active_401ks"]["income_1"]["employer_contribution_pct"]
        
        self.income_2_current_401k_value = self.input_data["investments"]["active_401ks"]["income_2"]["current_acct_value"]
        self.income_2_employee_contribution_rate = self.input_data["investments"]["active_401ks"]["income_2"]["employee_contribution_pct"]
        self.income_2_employer_contribution_rate = self.input_data["investments"]["active_401ks"]["income_2"]["employer_contribution_pct"]
        
        # IRAs
        self.ira_1_current_value = self.input_data["investments"]["ira_1"]["current_acct_value"]
        self.ira_1_current_monthly_contribution = self.input_data["investments"]["ira_1"]["current_monthly_contribution"]
        
        self.ira_2_current_value = self.input_data["investments"]["ira_2"]["current_acct_value"]
        self.ira_2_current_monthly_contribution = self.input_data["investments"]["ira_2"]["current_monthly_contribution"]
        

    # Saving Account Details
    
        self.savings_acct_1_current_value = self.input_data["savings"]["account_1"]["current_account_value"]
        self.savings_acct_1_current_account_interest_rate = self.input_data["savings"]["account_1"]["current_account_interest_rate"]
        self.savings_acct_1_income1_base_monthly_contribution = self.input_data["savings"]["account_1"]["income1_base_monthly_contribution"]
        self.savings_acct_1_income1_base_monthly_contribution_percent = self.input_data["savings"]["account_1"]["income1_base_monthly_contribution_percent"]
        self.savings_acct_1_income1_base_monthly_deduction = self.input_data["savings"]["account_1"]["income1_base_monthly_deduction"]
        self.savings_acct_1_income1_base_monthly_deduction_percent = self.input_data["savings"]["account_1"]["income1_base_monthly_deduction_percent"]
        self.savings_acct_1_income1_current_month_contribution = self.input_data["savings"]["account_1"]["income1_current_month_contribution"]
        self.savings_acct_1_income1_current_month_deduction = self.input_data["savings"]["account_1"]["income1_current_month_deduction"]
        self.savings_acct_1_income2_base_monthly_contribution = self.input_data["savings"]["account_1"]["income2_base_monthly_contribution"]
        self.savings_acct_1_income2_base_monthly_contribution_percent = self.input_data["savings"]["account_1"]["income2_base_monthly_contribution_percent"]
        self.savings_acct_1_income2_base_monthly_deduction = self.input_data["savings"]["account_1"]["income2_base_monthly_deduction"]
        self.savings_acct_1_income2_base_monthly_deduction_percent = self.input_data["savings"]["account_1"]["income2_base_monthly_deduction_percent"]
        self.savings_acct_1_income2_current_month_contribution = self.input_data["savings"]["account_1"]["income2_current_month_contribution"]
        self.savings_acct_1_income2_current_month_deduction = self.input_data["savings"]["account_1"]["income2_current_month_deduction"]
        
        self.savings_acct_2_current_value = self.input_data["savings"]["account_2"]["current_account_value"]
        self.savings_acct_2_current_account_interest_rate = self.input_data["savings"]["account_2"]["current_account_interest_rate"]
        self.savings_acct_2_income1_base_monthly_contribution = self.input_data["savings"]["account_2"]["income1_base_monthly_contribution"]
        self.savings_acct_2_income1_base_monthly_contribution_percent = self.input_data["savings"]["account_2"]["income1_base_monthly_contribution_percent"]
        self.savings_acct_2_income1_base_monthly_deduction = self.input_data["savings"]["account_2"]["income1_base_monthly_deduction"]
        self.savings_acct_2_income1_base_monthly_deduction_percent = self.input_data["savings"]["account_2"]["income1_base_monthly_deduction_percent"]
        self.savings_acct_2_income1_current_month_contribution = self.input_data["savings"]["account_2"]["income1_current_month_contribution"]
        self.savings_acct_2_income1_current_month_deduction = self.input_data["savings"]["account_2"]["income1_current_month_deduction"]
        self.savings_acct_2_income2_base_monthly_contribution = self.input_data["savings"]["account_2"]["income2_base_monthly_contribution"]
        self.savings_acct_2_income2_base_monthly_contribution_percent = self.input_data["savings"]["account_2"]["income2_base_monthly_contribution_percent"]
        self.savings_acct_2_income2_base_monthly_deduction = self.input_data["savings"]["account_2"]["income2_base_monthly_deduction"]
        self.savings_acct_2_income2_base_monthly_deduction_percent = self.input_data["savings"]["account_2"]["income2_base_monthly_deduction_percent"]
        self.savings_acct_2_income2_current_month_contribution = self.input_data["savings"]["account_2"]["income2_current_month_contribution"]
        self.savings_acct_2_income2_current_month_deduction = self.input_data["savings"]["account_2"]["income2_current_month_deduction"]
        
        self.cd_current_value = self.input_data["savings"]["cd"]["current_account_value"]
        self.cd_current_account_interest_rate = self.input_data["savings"]["cd"]["current_account_interest_rate"]
        self.cd_income1_base_monthly_contribution = self.input_data["savings"]["cd"]["income1_base_monthly_contribution"]
        self.cd_income1_base_monthly_contribution_percent = self.input_data["savings"]["cd"]["income1_base_monthly_contribution_percent"]
        self.cd_income1_base_monthly_deduction = self.input_data["savings"]["cd"]["income1_base_monthly_deduction"]
        self.cd_income1_base_monthly_deduction_percent = self.input_data["savings"]["cd"]["income1_base_monthly_deduction_percent"]
        self.cd_income1_current_month_contribution = self.input_data["savings"]["cd"]["income1_current_month_contribution"]
        self.cd_income1_current_month_deduction = self.input_data["savings"]["cd"]["income1_current_month_deduction"]
        self.cd_income2_base_monthly_contribution = self.input_data["savings"]["cd"]["income2_base_monthly_contribution"]
        self.cd_income2_base_monthly_contribution_percent = self.input_data["savings"]["cd"]["income2_base_monthly_contribution_percent"]
        self.cd_income2_base_monthly_deduction = self.input_data["savings"]["cd"]["income2_base_monthly_deduction"]
        self.cd_income2_base_monthly_deduction_percent = self.input_data["savings"]["cd"]["income2_base_monthly_deduction_percent"]
        self.cd_income2_current_month_contribution = self.input_data["savings"]["cd"]["income2_current_month_contribution"]
        self.cd_income2_current_month_deduction = self.input_data["savings"]["cd"]["income2_current_month_deduction"]
        
        
    # Tax Details
        self.marginal_tax_rate = self.input_data["taxes"]["marginal_tax_rate"]

    def define_incomes_assets_and_liabilities(self):
        
        self.income_1 = Income(
                            base_salary=self.income_1_base_amount,
                            paycheck_non401k_pre_tax_deductions=self.income_1_paycheck_non401k_pre_tax_deductions,
                            paycheck_schedule=self.income_1_pay_schedule,
                            pre_tax_401k_contribution_rate=self.income_2_401k_pretax_contribution_rate
                        )
        
        self.income_2 = Income(
                            base_salary=self.income_2_base_amount,
                            paycheck_non401k_pre_tax_deductions=self.income_2_paycheck_non401k_pre_tax_deductions,
                            paycheck_schedule=self.income_2_pay_schedule,
                            pre_tax_401k_contribution_rate=self.income_2_401k_pretax_contribution_rate
                        )
    
        self.mortgage = Mortgage(
                            origination_date=self.mortgage_origination_date, 
                            initial_upb=self.mortgage_initial_upb, 
                            interest_rate=self.mortgage_interest_rate, 
                            term=(self.mortgage_length*12), 
                            current_upb=self.mortgage_current_upb,
                            monthly_escrow=self.current_monthly_escrow,
                            recurring_prepayment=self.recurring_mortgage_prepayment,
                            one_time_prepayment=self.mortgage_one_time_prepayment
                        )
        
        self.student_loans = Loan(
                            origination_date= self.student_loan_origination_date,
                            interest_rate=self.student_loan_avg_interest_rate,
                            initial_upb=self.student_loan_initial_upb, 
                            term=(self.student_loan_term*12), # Convert to Months 
                            current_upb=self.student_loan_current_upb,
                            recurring_prepayment=self.student_loan_recurring_prepayment,
                            one_time_prepayment=self.student_loan_prepayment_this_month
                        )
        
        self.car_loan = Loan(
                        origination_date= self.car_loan_origination_date, 
                        initial_upb=self.car_loan_initial_upb,
                        interest_rate=self.car_loan_interest_rate, 
                        term=self.car_loan_term_length, 
                        current_upb=self.car_loan_current_upb,
                        one_time_prepayment=self.car_loan_one_time_prepayment,
                        recurring_prepayment=self.car_loan_recurring_prepayment
                    )
        
        self.savings_acct_1 = SavingsAccount(
                income_1=self.income_1,
                current_account_value=self.savings_acct_1_current_value, 
                income1_base_monthly_contribution=self.savings_acct_1_income1_base_monthly_contribution, 
                income1_base_monthly_deduction=self.savings_acct_1_income1_base_monthly_deduction, 
                current_account_interest_rate=self.savings_acct_1_current_account_interest_rate
                )
        
        self.savings_acct_2 = SavingsAccount(
                current_account_value=self.savings_acct_2_current_value, 
                income_1=self.income_1,
                income1_base_monthly_contribution=self.savings_acct_2_income1_base_monthly_contribution, 
                income1_base_monthly_deduction=self.savings_acct_2_income1_base_monthly_deduction, 
                current_account_interest_rate=self.savings_acct_2_current_account_interest_rate)
        
        self.cd = SavingsAccount(
                income_1=self.income_1,
                current_account_value=self.cd_current_value, 
                income1_base_monthly_contribution=self.cd_income1_base_monthly_contribution,
                income1_base_monthly_deduction=self.cd_income1_current_month_deduction,
                current_account_interest_rate=self.cd_current_account_interest_rate)
        
        self.person = FourZeroOneKay(income=self.income_1,
                                            existing_investment=75000,
                                            base_monthly_contribution_percent=0.00,
                                            employer_match_percent=0.00)
        fanniemae_401k = FourZeroOneKay(income=self.income_1, 
                                        existing_investment=4500, 
                                        base_monthly_contribution_percent=0.135,
                                        employer_match_percent=.08)
        ohio_state_403b = FourZeroOneKay(income=self.income_2,
                                        existing_investment=55000,
                                        base_monthly_contribution_percent=0.00,
                                        employer_match_percent=0.00)
        ohio_state_rollover = RothIRA(income=self.income_1, 
                                      existing_investment=19200)
        brokerage_account = EquityInvestment(6700, average_return=self.avg_equity_return)
    
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
    rollover_delta = projected_wealth.at[0, 'Income_1_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12) - projected_wealth.at[0, 'Income_1_Rollover_IRA_Value']
    ohio_state_delta = projected_wealth.at[0, 'Income_2_Rollover_IRA_value'] * (1 + ohio_state_403b.average_return / 12) - projected_wealth.at[0, 'Income_2_Rollover_IRA_value']
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
                                projected_wealth.at[0, 'Income_1_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12),
                                projected_wealth.at[0, 'Income_2_Rollover_IRA_value'] * (1 + ohio_state_403b.average_return / 12),
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
        rollover_delta = projected_wealth.at[i - 1, 'Income_1_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12) - projected_wealth.at[i - 1, 'Income_1_Rollover_IRA_Value']
        ohio_state_delta = projected_wealth.at[i - 1, 'Income_2_Rollover_IRA_value'] * (1 + ohio_state_403b.average_return / 12) - projected_wealth.at[i - 1, 'Income_2_Rollover_IRA_value']
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
                                    projected_wealth.at[i - 1, 'Income_1_Rollover_IRA_Value'] * (1 + ohio_state_rollover.average_return / 12),
                                    projected_wealth.at[i - 1, 'Income_2_Rollover_IRA_value'] * (1 + ohio_state_403b.average_return / 12),
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
            origination_date=mortgage_origination_date, 
            initial_upb=320100, 
            interest_rate=0.0299, 
            term=(12*30), 
            current_upb=289500,
            monthly_escrow=current_monthly_escrow,
            recorded_home_valuation=recorded_home_valuation,
            recurring_prepayment=0,
            one_time_prepayment=0)
        
        student_loans = Loan(
            origination_date=mortgage_origination_date,
            interest_rate=6.1,
            initial_upb=61000, 
            term=120,
            current_upb=50500,
            one_time_prepayment=0,
            recurring_prepayment=0)
        
        car_loans = Loan(
            origination_date=car_loan_origination_date, 
            initial_upb=14100,
            interest_rate=0.0499, 
            term=36, 
            current_upb=12700,
            recurring_prepayment=0,
            one_time_prepayment=0)
        emergency_savings_account = SavingsAccount(
            income_1=income_1,
            current_account_value=19000, 
            income1_base_monthly_contribution=0, 
            income1_base_monthly_deduction=0, 
            current_account_interest_rate=0.045)
        vacation_account = SavingsAccount(
            current_account_value=1500, 
            income_1=income_1,
            income1_base_monthly_contribution=400, 
            income1_base_monthly_deduction=0, 
            current_account_interest_rate=0.045)
        cd = SavingsAccount(
            income_1=income_1,
            current_account_value=25100, 
            income1_base_monthly_contribution=0,
            income1_base_monthly_deduction=0,
            current_account_interest_rate=0.055)
        income_1_roth = RothIRA(income=income_1,
                                existing_investment=75000,
                                base_monthly_contribution_percent=0.00,
                                employer_match_percent=0.00)
        income_1_401k = FourZeroOneKay(income=income_1, 
                                        existing_investment=4500,
                                        base_monthly_contribution_percent=0.135,
                                        employer_match_percent=.06)
        income_2_roth = RothIRA(income=income_1, 
                                existing_investment=18000,
                                base_monthly_contribution_percent=0.00,
                                employer_match_percent=0.00)
        brokerage_account = EquityInvestment(6700, average_return=avg_equity_return)
        
        total_wealth_sum = (
            emergency_savings_account.current_account_value +
            vacation_account.current_account_value +
            cd.current_account_value +
            income_1_roth.existing_investment +
            income_1_401k.existing_investment +
            income_2_roth.existing_investment +
            income_2_401k.existing_investment +
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
        'Emergency_Savings': [emergency_savings_account.current_account_value],
        'Vacation_Savings': [vacation_account.current_account_value],
        'CD': [cd.current_account_value],
        'Income_1_IRA1': [income_1_roth.existing_investment],
        'Income_1_401k': [income_1_401k.existing_investment],
        'Income_2_401k': [income_2_401k.existing_investment],
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
    
    wealth_forecast = WealthForecast()
    
    # Read in data
    input_file = Path("inputs.json")
    wealth_forecast.read_data(input_file)

    # Add income details
    wealth_forecast.add_income(
        Income(
            base_salary=income_1,
            paycheck_non401k_pre_tax_deductions= wealth_forecast,
            paycheck_schedule='biweekly',
            pre_tax_401k_contribution_rate=income_1_401k_pretax_contribution_rate
        )
    )
    wealth_forecast.add_income(
        Income(
        base_salary=income_2,
        paycheck_non401k_pre_tax_deductions= 30.00,
        paycheck_schedule='weekly',
        pre_tax_401k_contribution_rate=income_2_401k_pretax_contribution_rate
        )
    )
    
    # Read existing loan and investment data
    current_wealth_data = read_current_wealth(income_1=income_1_base, income_2=income_2_base)

    # Update projections for the next month
    forecast = monthly_forecasting(income_1=income_1_base, income_2=income_2_base, wealth_df=current_wealth_data)

    # Write updated projections to file
    write_current_wealth(current_wealth_data)

if __name__ == "__main__":
    main()
