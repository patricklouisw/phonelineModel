# import application as app
from datetime import *
from data1 import tiny_data
from test_data import jan_data, com_data, customer, loc_data, filter_data
from contract import *
from customer import *
from phoneline import *
from filter import *
import unittest
LOW_COOR = (-79.697878, 43.576959)
HIGH_COOR = (-79.196382, 43.799568)
def create_customers(log: Dict[str, List[Dict]]) -> List[Customer]:
    """ Returns a list of Customer instances for each customer from the input
    dataset from the dictionary <log>.

    Precondition:
    - The <log> dictionary contains the input data in the correct format,
    matching the expected input format described in the handout.
    """
    customer_list = []
    for cust in log['customers']:
        customer = Customer(cust['id'])
        for line in cust['lines']:
            contract = None

            if line['contract'] == 'prepaid':
                # start with $100 credit on the account
                contract = PrepaidContract(datetime.date(2017, 12, 25), 100)
            elif line['contract'] == 'mtm':
                contract = MTMContract(datetime.date(2017, 12, 25))
            elif line['contract'] == 'term':
                contract = TermContract(datetime.date(2017, 12, 25),
                                        datetime.date(2019, 6, 25))
            else:
                print("ERROR: unknown contract type")

            line = PhoneLine(line['number'], contract)
            customer.add_phone_line(line)
        customer_list.append(customer)
    return customer_list


def create_call(source: dict) -> List[Call]:
    res = []
    event_list = source["events"]
    for event_dict in event_list:
        if event_dict["type"] == "call":
            src_number = event_dict["src_number"]
            dst_number = event_dict["dst_number"]
            duration = event_dict["duration"]
            time = event_dict["time"]
            time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            src_loc = event_dict["src_loc"]
            dst_loc = event_dict["dst_loc"]
            call = Call(src_number, dst_number, time, duration, src_loc,
                        dst_loc)
            res.append(call)
    return res


class Test41(unittest.TestCase):
    def setUp(self):
        self.filter = CustomerFilter()
        self.customer = create_customers(customer)
        self.jan_call = create_call(filter_data)
        self.customer[3].make_call(self.jan_call[0])
        self.customer[1].make_call(self.jan_call[1])
        self.customer[3].make_call(self.jan_call[2])
        self.customer[4].receive_call(self.jan_call[0])
        self.customer[3].receive_call(self.jan_call[1])
        self.customer[3].receive_call(self.jan_call[2])

    def test_basic(self):
        act_res = self.filter.apply(self.customer, self.jan_call[-1:], "5716")
        exp_res = self.jan_call[-1:]
        self.assertCountEqual(exp_res, act_res, "Return every call in the list that have the same src-number / dst-number associated with numbers in Uers's phonlines")

    def test_basic_2(self):
        act_res = self.filter.apply(self.customer, self.jan_call, "9701")
        exp_res = []
        self.assertCountEqual(self.jan_call[0:1], act_res, "Return every call in the list that have the same src-number / dst-number associated with numbers in Uers's phonlines")
        act_res = self.filter.apply(self.customer, self.jan_call, "8548")
        self.assertCountEqual(exp_res, act_res, "Return every call in the list that have the same src-number / dst-number associated with numbers in Uers's phonlines")
        act_res = self.filter.apply(self.customer, self.jan_call, "2247")
        self.assertCountEqual(exp_res, act_res, "Return every call in the list that have the same src-number / dst-number associated with numbers in Uers's phonlines")

    def test_basic_3(self):
        act_res = self.filter.apply(self.customer, self.jan_call, "5716")
        exp_res = [self.jan_call[0], self.jan_call[1], self.jan_call[2]]
        self.assertCountEqual(exp_res, act_res, "Return every call in the list that have the same src-number / dst-number associated with numbers in Uers's phonlines")
        exp_res = [self.jan_call[1]]
        act_res = self.filter.apply(self.customer, self.jan_call, "3895")
        self.assertCountEqual(exp_res, act_res, "Return every call in the list that have the same src-number / dst-number associated with numbers in Uers's phonlines")

    def test_invalid(self):
        act_res = self.filter.apply(self.customer, self.jan_call[-1:], "sdhfsdjn")
        self.assertEqual(True, act_res == self.jan_call[-1:], "Return the orginal list since the user id is invalid")
        act_res = self.filter.apply(self.customer, self.jan_call[-1:], "")
        self.assertEqual(True, act_res == self.jan_call[-1:], "Return the orginal list since the user id is invalid")
        act_res = self.filter.apply(self.customer, self.jan_call[-1:], "abcd")
        self.assertEqual(True, act_res == self.jan_call[-1:], "Return the orginal list since the user id is invalid")
        act_res = self.filter.apply(self.customer, self.jan_call, "abc1")
        exp_res = self.jan_call
        self.assertCountEqual(exp_res, act_res, "Return the orginal list since the user id is invalid")
        act_res = self.filter.apply(self.customer, self.jan_call, "9999")
        self.assertEqual(True, act_res == self.jan_call, "Return the orginal list since the user id is invalid")


class Test42(unittest.TestCase):
    def setUp(self):
        self.filter = DurationFilter()
        self.customer = create_customers(customer)
        self.jan_call = create_call(filter_data)
        self.customer[3].make_call(self.jan_call[0])
        self.customer[1].make_call(self.jan_call[1])
        self.customer[3].make_call(self.jan_call[2])
        self.customer[4].receive_call(self.jan_call[0])
        self.customer[3].receive_call(self.jan_call[1])
        self.customer[3].receive_call(self.jan_call[2])

    def test_basic(self):
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "L120")
        exp_res = [self.jan_call[0]]
        self.assertCountEqual(exp_res, act_res, "Return every call in the list which less than 120")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "G120")
        self.assertCountEqual([], act_res, "Return every call in the list which grater than 120")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], 'G100')
        self.assertCountEqual(exp_res, act_res, "Return every call in the list which grater than 100")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "L100")
        self.assertCountEqual([], act_res, "Return every call in the list which less than 100")

    def test_basic_2(self):
        act_res = self.filter.apply(self.customer, self.jan_call, "G110")
        self.assertCountEqual(self.jan_call,act_res, "Return every call in the list which grater than 120")
        act_res = self.filter.apply(self.customer, self.jan_call, "L120")
        self.assertCountEqual(self.jan_call, act_res, "Return every call in the list which less than 120")
        act_res = self.filter.apply(self.customer, self.jan_call, "L100")
        self.assertCountEqual([], act_res, "Return every call in the list which less than 100")
        act_res = self.filter.apply(self.customer, self.jan_call, "G200")
        self.assertCountEqual([], act_res, "Return every call in the list which grater than 200")
        act_res = self.filter.apply(self.customer, self.jan_call, "G50")
        self.assertEqual(self.jan_call, act_res, "Return every call in the list greater than 50")
        act_res = self.filter.apply(self.customer, self.jan_call, "L1")
        self.assertEqual([], act_res, "Return empty list")

    def test_basic_3(self):
        act_res = self.filter.apply(self.customer, self.jan_call, "L118")
        exp_res = [self.jan_call[-1]]
        self.assertCountEqual(exp_res, act_res, "Return every call in the list which less than 118")
        act_res = self.filter.apply(self.customer, self.jan_call, "G118")
        self.assertCountEqual([self.jan_call[1]], act_res, "Return every call in the list which grater than 118")
        act_res = self.filter.apply(self.customer, self.jan_call, "L119")
        exp_res = [self.jan_call[0], self.jan_call[-1]]
        self.assertCountEqual(exp_res, act_res, "Return every call in the list which less than 119")
        act_res = self.filter.apply(self.customer, self.jan_call, "L120")
        self.assertCountEqual(self.jan_call, act_res, "Return every call in the list which less than 120")
        act_res = self.filter.apply(self.customer, self.jan_call, "G117")
        exp_res = self.jan_call[0:2]
        self.assertCountEqual(exp_res, act_res, "Return every call in the list which greater than 117")

    def test_invalid(self):
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "sdhfsdjn")
        self.assertEqual(True, act_res == [self.jan_call[0]], "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "")
        self.assertEqual(True, act_res == [self.jan_call[0]], "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "g131")
        self.assertEqual(True, act_res == [self.jan_call[0]], "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "l999")
        self.assertEqual(True, act_res == [self.jan_call[0]], "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "Lb99")
        self.assertEqual(True, act_res == [self.jan_call[0]], "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, [self.jan_call[0]], "G9b9")
        self.assertEqual(True, act_res == [self.jan_call[0]], "Return the orginal list since the filter string is invalid")




class Test43(unittest.TestCase):
    def setUp(self):
        self.filter = LocationFilter()
        self.customer = create_customers(customer)
        self.jan_call = create_call(jan_data)
        self.loc_data = create_call(loc_data)
        self.customer[3].make_call(self.loc_data[0])
        self.customer[1].make_call(self.loc_data[1])
        self.customer[3].make_call(self.loc_data[2])
        self.customer[4].receive_call(self.loc_data[0])
        self.customer[3].receive_call(self.loc_data[1])
        self.customer[3].receive_call(self.loc_data[2])

    def test_basic_1(self):
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "-79.68, 43.6, -79.679, 43.7")
        self.assertCountEqual([], act_res, "Return every call in the list in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "-79.7, 43.6, -79.5, 43.64")
        self.assertCountEqual(self.loc_data[-1:], act_res, "Return empty list since neither the src not dst are in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-100, 80, -50, 90")
        self.assertEqual(self.loc_data, act_res, "Return everything")

    def test_basic_2(self):
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.5, 43.61, -79.2, 43.799")
        exp_res = self.loc_data[1:]
        self.assertCountEqual(exp_res, act_res, "Return the call in the list within the given boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.21, 43.58, -79.20, 43.68")
        self.assertCountEqual([], act_res, "Return empty list")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.60, 43.577, -79.2, 43.78")
        self.assertCountEqual(self.loc_data, act_res, "Return every call in the list in the boundary")

    def test_basic_3(self):
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.68, 43.58, -79.679, 43.581")
        self.assertCountEqual([], act_res, "Return empty list")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.60, 43.58, -79.58, 43.60")
        self.assertCountEqual(self.loc_data[0:1], act_res, "Return the call in the boundary even only src is in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.58, 43.58, -79.579, 43.581")
        self.assertCountEqual(self.loc_data[0:1], act_res, "Return the call in the boundary even only dst is in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.479, 43.62, -79.39, 43.641")
        self.assertCountEqual(self.loc_data[1:2], act_res, "Return the call in the boundary even only src is in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.47, 43.63, -79.39, 43.64")
        self.assertCountEqual(self.loc_data[1:2], act_res, "Return the call in the boundary even only dst is in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.58, 43.58, -79.479, 43.62")
        exp_res = self.loc_data[0:2]
        self.assertCountEqual(exp_res, act_res, "Return calls in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.49, 43.59, -79.39, 43.64")
        self.assertCountEqual(exp_res, act_res, "Return calls in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.48, 43.63, -79.379, 43.661")
        exp_res = self.loc_data[1:3]
        self.assertCountEqual(exp_res, act_res, "Return calls in the boundary")
        act_res = self.filter.apply(self.customer, self.loc_data, "-79.60, 43.58, -79.29, 43.67")
        exp_res = self.loc_data
        self.assertCountEqual(exp_res, act_res, "Return calls in the boundary")


    def test_invalid(self):
        act_res = self.filter.apply(self.customer, self.loc_data, "-100, 40, -100, 40")
        self.assertEqual(True, act_res == self.loc_data, "Return the original list since it out of boundary")
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "sdhfsdjn")
        self.assertEqual(True, act_res == self.loc_data[-1:],
                              "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "")
        self.assertEqual(True, act_res == self.loc_data[-1:],
                              "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "abcd, bcde, fghi")
        self.assertEqual(True, act_res == self.loc_data[-1:],
                              "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "abcd, bcde, gfik, xksd")
        self.assertEqual(True, act_res == self.loc_data[-1:],
                              "Return the orginal list since the filter string is invalid")
        act_res = self.filter.apply(self.customer, self.loc_data[-1:], "123b, 456c, 321d, 459s")
        self.assertEqual(True, act_res == self.loc_data[-1:],
                              "Return the orginal list since the filter string is invalid")

unittest.main(exit=False)

