import datetime
import pytest

from application import create_customers, process_event_history
from customer import Customer
from contract import TermContract, MTMContract, PrepaidContract
from phoneline import PhoneLine
from filter import DurationFilter, CustomerFilter, ResetFilter
from typing import List

"""
This is a sample test file with a limited set of cases, which are similar in
nature to the full autotesting suite

Use this framework to check some of your work and as a starting point for
creating your own tests

*** Passing these tests does not mean that it will necessarily pass the
autotests ***
"""


def create_two_customer_with_all_lines() -> List[Customer]:
    """ Create a customer with one of each type of PhoneLine
    """
    contracts = [
        TermContract(start=datetime.date(year=2017, month=12, day=25),
                     end=datetime.date(year=2019, month=6, day=25)),
        MTMContract(start=datetime.date(year=2017, month=12, day=25)),
        PrepaidContract(start=datetime.date(year=2017, month=12, day=25),
                        balance=100)
    ]
    numbers = ['123-4567', '987-6543', '654-3210', '246-8101', '135-7911',
               '112-3581']
    customer1 = Customer(cid=6666)
    customer2 = Customer(cid=7777)

    for i in range(len(contracts)):
        customer1.add_phone_line(PhoneLine(numbers[i], contracts[i]))

    # create another customer with different phone number but same contracts
    for i in range(len(contracts)):
        customer2.add_phone_line(PhoneLine(numbers[i + 3], contracts[i]))

    customer1.new_month(12, 2017)
    customer2.new_month(12, 2017)
    return [customer1, customer2]


# each customer made a single call using each phone line.
test_dict = {'events': [
    {"type": "sms",
     "src_number": "123-4567",
     "dst_number": "246-8101",
     "time": "2018-01-26 01:01:01",
     "src_loc": [-79.6, 43.7],
     "dst_loc": [-79.42, 43.59]},
    {"type": "sms",
     "src_number": "987-6543",
     "dst_number": "135-7911",
     "time": "2018-01-23 01:01:02",
     "src_loc": [-79.5, 43.62],
     "dst_loc": [-79.5, 43.71]},

    {"type": "call",
     "src_number": "123-4567",
     "dst_number": "246-8101",
     "time": "2018-02-16 01:01:04",
     "duration": 6120,
     "src_loc": [-79.4, 43.65],
     "dst_loc": [-79.5, 43.78]},
    {"type": "call",
     "src_number": "987-6543",
     "dst_number": "135-7911",
     "time": "2018-02-04 01:01:05",
     "duration": 120,
     "src_loc": [-79.3, 43.79],
     "dst_loc": [-79.5, 43.72]},
    {"type": "call",
     "src_number": "654-3210",
     "dst_number": "112-3581",
     "time": "2018-03-09 01:01:06",
     "duration": 240000,
     "src_loc": [-79.2, 43.66],
     "dst_loc": [-79.5, 43.74]},
    {"type": "call",
     "src_number": "246-8101",
     "dst_number": "123-4567",
     "time": "2018-03-06 01:01:04",
     "duration": 6000,
     "src_loc": [-79.34, 43.6],
     "dst_loc": [-79.22, 43.77]},
    {"type": "call",
     "src_number": "135-7911",
     "dst_number": "987-6543",
     "time": "2018-04-15 01:01:05",
     "duration": 230,
     "src_loc": [-79.34, 43.68],
     "dst_loc": [-79.57, 43.7]},
    {"type": "call",
     "src_number": "112-3581",
     "dst_number": "654-3210",
     "time": "2018-04-21 01:01:06",
     "duration": 290,
     "src_loc": [-79.4, 43.61],
     "dst_loc": [-79.5, 43.75]}
    ],
    'customers': [
    {'lines': [
        {'number': '123-4567',
         'contract': 'term'},
        {'number': '987-6543',
         'contract': 'mtm'},
        {'number': '654-3210',
         'contract': 'prepaid'}
    ],
     'id': 6666},
    {'lines': [
        {'number': '246-8101',
         'contract': 'term'},
        {'number': '135-7911',
         'contract': 'mtm'},
        {'number': '112-3581',
         'contract': 'prepaid'}
    ],
     'id': 7777}
    ]
}


def test_customer_creation() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """
    # customers list of Customer
    customers = create_two_customer_with_all_lines()
    bill1 = customers[0].generate_bill(12, 2017)
    bill2 = customers[1].generate_bill(12, 2017)

    assert len(customers[0].get_phone_numbers()) == 3
    assert len(customers[1].get_phone_numbers()) == 3
    assert len(bill1) == 3
    assert len(bill2) == 3
    assert bill1[0] == 6666
    assert bill2[0] == 7777
    assert bill1[1] == 270.0
    assert bill2[1] == 270.0
    assert len(bill1[2]) == 3
    assert len(bill2[2]) == 3
    assert bill1[2][0]['total'] == 320
    assert bill1[2][1]['total'] == 50
    assert bill1[2][2]['total'] == -100
    assert bill2[2][0]['total'] == 320
    assert bill2[2][1]['total'] == 50
    assert bill2[2][2]['total'] == -100

    # Check for the customer creation in application.py
    customer1 = create_customers(test_dict)[0]
    customer2 = create_customers(test_dict)[1]
    customer1.new_month(12, 2017)
    customer2.new_month(12, 2017)
    bill1 = customer1.generate_bill(12, 2017)
    bill2 = customer2.generate_bill(12, 2017)

    assert len(customer1.get_phone_numbers()) == 3
    assert len(customer2.get_phone_numbers()) == 3
    assert len(bill1) == 3
    assert len(bill2) == 3
    assert bill1[0] == 6666
    assert bill2[0] == 7777
    assert len(bill1[2]) == 3
    assert len(bill2[2]) == 3
    assert bill1[2][0]['total'] == 320
    assert bill1[2][1]['total'] == 50
    assert bill1[2][2]['total'] == -100
    assert bill2[2][0]['total'] == 320
    assert bill2[2][1]['total'] == 50
    assert bill2[2][2]['total'] == -100


def test_events() -> None:
    """ Test the ability to make calls, and ensure that the CallHistory objects
    are populated
    """
    customers = create_customers(test_dict)
    customers[0].new_month(1, 2018)
    customers[1].new_month(1, 2018)

    process_event_history(test_dict, customers)

    # Check bills for each month for each customer
    cust1_bill1 = customers[0].generate_bill(1, 2018)
    cust1_bill2 = customers[0].generate_bill(2, 2018)
    cust1_bill3 = customers[0].generate_bill(3, 2018)
    cust1_bill4 = customers[0].generate_bill(4, 2018)
    cust2_bill1 = customers[1].generate_bill(1, 2018)
    cust2_bill2 = customers[1].generate_bill(2, 2018)
    cust2_bill3 = customers[1].generate_bill(3, 2018)
    cust2_bill4 = customers[1].generate_bill(4, 2018)

    assert cust1_bill1[0] == 6666
    assert cust1_bill2[0] == 6666
    assert cust1_bill3[0] == 6666
    assert cust1_bill4[0] == 6666

    assert cust2_bill1[0] == 7777
    assert cust2_bill2[0] == 7777
    assert cust2_bill3[0] == 7777
    assert cust2_bill4[0] == 7777

    assert cust1_bill1[1] == pytest.approx(-29.925)
    assert cust1_bill2[1] == pytest.approx(-29.925)
    assert cust1_bill3[1] == pytest.approx(-29.925)
    assert cust1_bill4[1] == pytest.approx(-29.925)

    assert cust2_bill1[1] == pytest.approx(-29.925)
    assert cust2_bill2[1] == pytest.approx(-29.925)
    assert cust2_bill3[1] == pytest.approx(-29.925)
    assert cust1_bill4[1] == pytest.approx(-29.925)

    assert cust1_bill1[2][0]['total'] == pytest.approx(20)
    assert cust1_bill2[2][0]['total'] == pytest.approx(20)
    assert cust1_bill3[2][0]['total'] == pytest.approx(20)
    assert cust1_bill4[2][0]['total'] == pytest.approx(20)

    assert cust2_bill1[2][0]['total'] == pytest.approx(20)
    assert cust2_bill2[2][0]['total'] == pytest.approx(20)
    assert cust2_bill3[2][0]['total'] == pytest.approx(20)
    assert cust2_bill4[2][0]['total'] == pytest.approx(20)

    assert cust1_bill1[2][0]['free_mins'] == 1
    assert cust1_bill2[2][0]['free_mins'] == 1
    assert cust1_bill3[2][0]['free_mins'] == 1
    assert cust1_bill4[2][0]['free_mins'] == 1

    assert cust2_bill1[2][0]['free_mins'] == 1
    assert cust2_bill2[2][0]['free_mins'] == 1
    assert cust2_bill3[2][0]['free_mins'] == 1
    assert cust2_bill4[2][0]['free_mins'] == 1

    assert cust1_bill1[2][1]['total'] == pytest.approx(50.05)
    assert cust1_bill2[2][1]['total'] == pytest.approx(50.05)
    assert cust1_bill3[2][1]['total'] == pytest.approx(50.05)
    assert cust1_bill4[2][1]['total'] == pytest.approx(50.05)

    assert cust2_bill1[2][1]['total'] == pytest.approx(50.05)
    assert cust2_bill2[2][1]['total'] == pytest.approx(50.05)
    assert cust2_bill3[2][1]['total'] == pytest.approx(50.05)
    assert cust2_bill4[2][1]['total'] == pytest.approx(50.05)

    assert cust1_bill1[2][1]['billed_mins'] == 1
    assert cust1_bill2[2][1]['billed_mins'] == 1
    assert cust1_bill3[2][1]['billed_mins'] == 1
    assert cust1_bill4[2][1]['billed_mins'] == 1

    assert cust2_bill1[2][1]['billed_mins'] == 1
    assert cust2_bill2[2][1]['billed_mins'] == 1
    assert cust2_bill3[2][1]['billed_mins'] == 1
    assert cust1_bill4[2][1]['billed_mins'] == 1

    assert cust1_bill1[2][2]['total'] == pytest.approx(-99.975)
    assert cust1_bill2[2][2]['total'] == pytest.approx(-99.975)
    assert cust1_bill3[2][2]['total'] == pytest.approx(-99.975)
    assert cust1_bill4[2][2]['total'] == pytest.approx(-99.975)

    assert cust2_bill1[2][2]['total'] == pytest.approx(-99.975)
    assert cust2_bill2[2][2]['total'] == pytest.approx(-99.975)
    assert cust2_bill3[2][2]['total'] == pytest.approx(-99.975)
    assert cust2_bill4[2][2]['total'] == pytest.approx(-99.975)

    assert bill1[2][2]['billed_mins'] == 1

    # Check the CallHistory objects are populated
    history = customers[0].get_call_history('867-5309')
    assert len(history) == 1
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1

    history = customers[0].get_call_history()
    assert len(history) == 3
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1


if __name__ == '__main__':
    pytest.main(['MY_TESTS.py'])
