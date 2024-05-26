def calculate_amortization_schedule(self, prepayment_this_month: int = 0):
        monthly_interest_rate = self.interest_rate / 12
        monthly_payment = (self.current_upb * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -self.term)

        remaining_balance = self.current_upb
        amortization_schedule = pd.DataFrame(columns=['Month', 'Payment', 'Interest', 'Principal', 'Balance'])

        for month in range(1, int(self.term) + 1):
            next_month_date = (datetime.strptime(self.origination_date, "%m-%Y") + pd.DateOffset(months=i)).strftime('%m-%Y')
            interest_payment = remaining_balance * monthly_interest_rate
            if prepayment_this_month > 0:
                principal_payment = monthly_payment + prepayment_this_month - interest_payment
            else:
                principal_payment = monthly_payment - interest_payment
                remaining_balance -= principal_payment
                
            amortization_schedule.loc[month] = [
                next_month_date,
                principal_payment + interest_payment,
                interest_payment,
                principal_payment,
                amortization_schedule.at[month - 1, 'Mortgage_UPB'] - principal_payment
            ]

        df = pd.DataFrame(amortization_schedule)
        return df