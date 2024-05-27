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