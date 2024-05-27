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