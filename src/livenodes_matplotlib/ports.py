import numbers
from livenodes.components.port import Port
from typing import NamedTuple
import numpy as np


class Port_Data(Port):

    example_values = [
        np.array([[[1]]])
    ]

    def __init__(self, name='Data', optional=False):
        super().__init__(name, optional)

    @staticmethod
    def check_value(value):
        if not isinstance(value, np.ndarray):
            return False, "Should be numpy array;"
        elif len(value.shape) != 3:
            return False, "Shape should be of length three (Batch, Time, Channel);"
        return True, None


class Port_Single_Channel_Int(Port):

    example_values = [
        0,
        1
    ]

    def __init__(self, name='Trigger', optional=False):
        super().__init__(name, optional)

    @staticmethod
    def check_value(value):
        if type(value) != int:
            return False, "Should be int;"
        return True, None


class Port_Single_Channel_Number(Port):

    example_values = [
        0,
        0.5,
        20
    ]

    def __init__(self, name='Trigger', optional=False):
        super().__init__(name, optional)

    @staticmethod
    def check_value(value):
        if not isinstance(value, numbers.Number):
            return False, "Should be number;"
        return True, None


class Port_Vector_of_Strings(Port):

    example_values = [
        ["EMG1", "EMG2"]
    ]

    def __init__(self, name='Channel Names', optional=False):
        super().__init__(name, optional)

    @staticmethod
    def check_value(value):
        if not (type(value) == list and type(value[0]) == str):
            return False, "Should be list of strings;"
        elif len(set(value)) != len(value):
            return False, "There should not be any duplicates;"
        return True, None


class Port_Vector_of_Ints(Port):

    example_values = [
        [0, 1, 20, -15]
    ]

    def __init__(self, name='File', optional=False):
        super().__init__(name, optional)

    @staticmethod
    def check_value(value):
        if not (type(value) == list and type(value[0]) == int):
            return False, "Should be list of ints;"
        return True, None


class Port_Dict(Port):

    example_values = [
        {},
        {'name': 'f', 'va': 5}
    ]

    def __init__(self, name='Meta', optional=False):
        super().__init__(name, optional)

    @staticmethod
    def check_value(value):
        if type(value) != dict:
            return False, "Should be dict;"
        return True, None





class Ports_empty(NamedTuple):
    pass

class Ports_data(NamedTuple):
    data: Port_Data = Port_Data("Data")


class Ports_data_channels(NamedTuple):
    data: Port_Data = Port_Data("Data")
    channels: Port_Vector_of_Strings = Port_Vector_of_Strings("Channel Names")
