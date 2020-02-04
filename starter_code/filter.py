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
import time
import datetime
from typing import List, Tuple
from call import Call
from customer import Customer


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """
    def __init__(self) -> None:
        pass

    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


def _helper1(customers: List[Customer], data: List[Call],
             filtering_id: int) -> List[Call]:
    """Simplify customer filtering."""
    new_data = []
    ever_reached = False
    for calls in data:
        for cust in customers:
            if cust.get_id() == filtering_id:
                ever_reached = True
                _helper2(calls, cust, new_data)
    if ever_reached:
        return new_data
    else:
        return data


def _helper2(calls: Call, cust: Customer, new_data: list) -> None:
    """Help the helper."""
    if calls in cust.get_history()[0] or calls in \
            cust.get_history()[1]:
        if calls not in new_data:
            new_data.append(calls)


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data> made or received by the
         customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.
        """
        try:
            filtering_id = int(filter_string)
        except ValueError:
            pass
        else:
            data = _helper1(customers, data, filtering_id)
        return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


def _helper3(duration: int, filter_string: str, data: List[Call]) -> List[Call]:
    """Help location filter."""
    if duration >= 0:
        new_data = []
        _helper4(filter_string, data, new_data, duration)
        return new_data
    return data


def _helper4(filter_string: str, data: List[Call], new_data: list,
             duration: int) -> None:
    """Help the helper3."""
    if filter_string[0] == "G":
        for calls in data:
            if calls.duration > duration:
                new_data.append(calls)
    elif filter_string[0] == "L":
        for calls in data:
            if calls.duration < duration:
                new_data.append(calls)


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data> with a duration of under or
        over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.
        """
        if len(filter_string) >= 2 and filter_string[0] in ["L", "G"]:
            string_duration = filter_string[1:]
            try:
                duration = int(string_duration)
            except ValueError:
                pass
            else:
                data = _helper3(duration, filter_string, data)
        return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


def _helper5(data: List[Call], coordinate_list: List[float],
             new_data: list) -> None:
    """Help the location filter."""
    for calls in data:
        if coordinate_list[0] <= calls.src_loc[0] <= \
                coordinate_list[2] and coordinate_list[1] <= \
                calls.src_loc[1] <= coordinate_list[3]:
            new_data.append(calls)
        elif coordinate_list[0] <= calls.dst_loc[0] <= \
                coordinate_list[2] and coordinate_list[1] <= \
                calls.dst_loc[1] <= coordinate_list[3]:
            new_data.append(calls)


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data>, which took place within
        a location specified by the <filter_string> (at least the source or the
        destination of the event was in the range of coordinates from the
        <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.
        """
        try:
            coordinate_list = []
            item_list = filter_string.split(",")
            for item in item_list:
                coordinate_list.append(float(item))
        except ValueError:
            pass
        else:
            if len(coordinate_list) == 4:
                if -79.697878 <= coordinate_list[0] <= -79.196382 and\
                        43.576959 <= coordinate_list[1] <= 43.799568 and\
                        -79.697878 <= coordinate_list[2] <= -79.196382 and\
                        43.576959 <= coordinate_list[3] <= 43.799568 and\
                        coordinate_list[0] <= coordinate_list[2] and\
                        coordinate_list[1] <= coordinate_list[3]:
                    new_data = []
                    _helper5(data, coordinate_list, new_data)
                    data = new_data
        return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
