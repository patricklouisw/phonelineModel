"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from typing import Optional
from math import ceil
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ A  Term Contract for a phone line

        === Public Attributes ===
        end:
             ending date for the contract

        === Private Attributes ===
        _cancellation_date:
             the last date a call was recorded
        """
    end: datetime.date
    _cancellation_date: datetime.date

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new Term Contract with the <start> date and ends at <end>,
        starts as inactive.
        """
        Contract.__init__(self, start)
        self.end = end
        self._cancellation_date = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self._cancellation_date = datetime.date(year, month, 1)
        self.bill = bill
        if [self.start.month, self.start.year] == [month, year]:
            self.bill.add_fixed_cost(TERM_DEPOSIT)
        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)
        self.bill.set_rates("TERM", TERM_MINS_COST)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        if self.bill.free_min < TERM_MINS:
            self.bill.add_free_minutes(ceil(call.duration / 60.0))
            if self.bill.free_min > TERM_MINS:
                extra = self.bill.free_min - TERM_MINS
                self.bill.free_min = TERM_MINS
                self.bill.add_billed_minutes(extra)
        else:
            Contract.bill_call(self, call)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract, if the end date for the term has passed, refund the
        deposit.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        if self._cancellation_date > self.end:
            self.end = None
            return self.bill.get_cost() - TERM_DEPOSIT
        else:
            self.end = None
            return self.bill.get_cost()


class MTMContract(Contract):
    """ A  Month to Month Contract for a phone line"""

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)
        self.bill.set_rates("MTM", MTM_MINS_COST)


class PrepaidContract(Contract):
    """ A  Prepaid Contract for a phone line

            === Public Attributes ===
            balance:
                 amount of money owed by this customer, if negative then it's
                 the amount of credit in the customers account
            """
    balance: float

    def __init__(self, start: datetime.date, balance: float) -> None:
        """ Create a new Prepaid Contract with the <start> date.
        Starts as inactive.
        """
        Contract.__init__(self, start)
        self.balance = - balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        Precondition: The first month is always initiated with more than $10
        credit.
        """
        if self.bill is None:
            self.bill = bill
            self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
            self.bill.add_fixed_cost(self.balance)
        else:
            self.balance = self.bill.get_cost()
            if self.balance > -10:
                self.balance -= 25
            self.bill = bill
            self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
            self.bill.add_fixed_cost(self.balance)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.If the customer has credit left, forfeit it.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        self.balance = 0
        if self.bill.get_cost() > 0:
            return self.bill.get_cost()
        else:
            return 0.0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
