"""
    Project :
        shared data types

    - color (r g b a)
    - vector (x y z)
    - event (...)

    change log [08/10/2024]:
    - added copy() for vector and colors
"""

# region : Includes

from functools import wraps
import imgui

# endregion


# region : Static functions

def linear(start_value, end_value, interpolation, hold: float = 0.01):
    """
        Linear interpolation function
    """

    if start_value == end_value:
        return end_value

    delta = end_value - start_value
    delta = delta * interpolation
    delta = delta + start_value

    if abs(delta - end_value) < hold:
        return end_value

    return delta


def clamp(value, min_value, max_value):
    """
        Clamp value function
    """

    if value > max_value:
        return max_value

    if value < min_value:
        return min_value

    return value


def safe_call(call_on_fail: any = None):
    """
        Safe call wrapper for functions
    """

    def decorator(function):
        @wraps(function)
        def safe_fn(*args, **kwargs):

            try:
                return function(*args, **kwargs)

            except Exception as e:

                error_msg = f"Found error in function {function.__name__}:\n{e}"

                if call_on_fail is not None:
                    call_on_fail(error_msg)

                return None

        return safe_fn

    return decorator

# endregion


# region : GUI utils types

class color:
    """
        Color RGBA object

        each field 0-255
    """

    r: int
    g: int
    b: int
    a: int

    def __init__(self, r=255, g=255, b=255, a=255):
        """
            Constructor for color object
        """

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __mul__(self, new_mult) -> any:
        """
            Overrides operator * to override alpha with value from 0 - 1
        """

        return color(self.r, self.g, self.b, self.a * new_mult)

    def unpack(self) -> tuple:
        """
            Unpacks the color values and returns as tuple the values
        """

        return self.r, self.g, self.b, self.a

    def copy(self):
        """
            Create a new instance copy of current color
        """

        return color(self.r, self.g, self.b, self.a)

    def lerp(self, other, weight: float, hold: float = 0.01):
        """
            Handle a linear interpolation between colors
        """

        new_r = linear(self.r, other.r, weight, hold)
        new_g = linear(self.g, other.g, weight, hold)
        new_b = linear(self.b, other.b, weight, hold)
        new_a = linear(self.a, other.a, weight, hold)

        return color(new_r, new_g, new_b, new_a)

    def __call__(self):
        """
            Function to return an u32 color type for ImGui Render
        """

        return imgui.get_color_u32_rgba(self.r / 255, self.g / 255, self.b / 255, self.a / 255)

    def __str__(self):
        """
            ToString override function
        """

        return f"color({self.r}, {self.g}, {self.b}, {self.a})"


class vector:
    """
        Vector 3D object

        each field float
    """

    x: float
    y: float
    z: float

    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        """
            Constructor for vector object
        """

        self.x = x
        self.y = y
        self.z = z

    def lerp(self, other, weight: float, hold: float = 0.01):
        """
            Handle a linear interpolation between vectors
        """

        new_x = linear(self.x, other.x, weight, hold)
        new_y = linear(self.y, other.y, weight, hold)
        new_z = linear(self.z, other.z, weight, hold)

        # Can also just override existing
        return vector(new_x, new_y, new_z)

    def unpack(self) -> tuple:
        """
            Unpacks all the vector values and returns as tuple the values
        """

        return self.x, self.y, self.z

    def unpack_2d(self) -> tuple:
        """
            Unpacks the vector x and y values and returns as tuple
        """
        return self.x, self.y

    def copy(self):
        """
            Create a new copy of vector with the same values
        """

        return vector(self.x, self.y, self.z)

    def is_in_bounds(self, start_vector, add_x, add_y) -> bool:
        """
            Checks if this vector is between 2 other vectors creating a rect area
        """

        if self.x < start_vector.x or self.x > (start_vector.x + add_x):
            return False

        if self.y < start_vector.y or self.y > (start_vector.y + add_y):
            return False

        return True

    def is_zero(self):
        """
            Checks if this vector is zero vector
        """

        return self.x == 0 and self.y == 0 and self.z == 0

    def as_tuple(self, vec: tuple):
        """
            Receives a tuple fulled with data like a vector,
            and convert it to a vector type
        """

        self.x = vec[0]
        self.y = vec[1]

        if 2 in vec:
            self.z = vec[2]

        return self

    def __str__(self):
        """
            ToString override function
        """

        return f"vector({self.x}, {self.y}, {self.z})"

    # region : Override operators

    def __add__(self, other: any):
        other_type = type(other)
        if other_type == vector:
            return vector(self.x + other.x, self.y + other.y, self.z + other.z)

        if other_type == int or other_type == float:
            return vector(self.x + other, self.y + other, self.z + other)

        raise Exception("Invalid other data type. Must be vector / int / float")

    def __sub__(self, other):
        other_type = type(other)
        if other_type == vector:
            return vector(self.x - other.x, self.y - other.y, self.z - other.z)

        if other_type == int or other_type == float:
            return vector(self.x - other, self.y - other, self.z - other)

        raise Exception("Invalid other data type. Must be vector / int / float")

    def __mul__(self, other):
        other_type = type(other)
        if other_type == vector:
            return vector(self.x * other.x, self.y * other.y, self.z * other.z)

        if other_type == int or other_type == float:
            return vector(self.x * other, self.y * other, self.z * other)

        raise Exception("Invalid other data type. Must be vector / int / float")

    def __truediv__(self, other):
        other_type = type(other)
        if other_type == vector:
            return vector(self.x / other.x, self.y / other.y, self.z / other.z)

        if other_type == int or other_type == float:
            return vector(self.x / other, self.y / other, self.z / other)

        raise Exception("Invalid other data type. Must be vector / int / float")

    def __eq__(self, other):
        other_type = type(other)
        if other_type == vector:
            return self.x == other.x and self.y == other.y and self.z == other.z

        if other_type == tuple:
            return self.x == other[0] and self.y == other[1] and self.z == other[2]

        raise Exception("Invalid other data type. Must be vector / tuple")

    # endregion


class event:
    """
        Event object

        Very usefull to handle multiple functions that should be
        executed all at once with the same arguments.
    """

    _event_data:        dict    # Event shared data
    _event_functions:   dict    # Event callbacks

    def __init__(self):
        """
            Constructor for event object
        """

        # Setup event data handler
        self._event_data = {}

        # Setup event functions handler
        self._event_functions = {}

    def __get(self, index) -> any:
        """
            Receive event specific data.
            Called within event callbacks
        """

        if index in self._event_data:
            return self._event_data[index]

        return None

    def __call__(self):
        """
            Execute the event and call all the functions
        """

        for function_name in self._event_functions:
            method_data = self._event_functions[function_name]

            # TODO ! maybe add safe call
            if method_data["allow_args"]:
                method_data["method"](self.__get)
            else:
                method_data["method"]()

    def __add__(self, information: tuple):
        """
            Adds data / callback functions to the event
        """

        data_len: int = len(information)

        if data_len == 2:
            # We want to add/update information
            self._event_data[information[0]] = information[1]

            return

        if data_len == 3:
            # We want to add function
            self._event_functions[information[1]] = {
                "method": information[0],
                "allow_args": information[2]
            }

            return

        raise Exception("Invalid data structure added")

    def __sub__(self, other: str):
        """
            Removes a specific function from callbacks
        """

        del self._event_functions[other]

# endregion
