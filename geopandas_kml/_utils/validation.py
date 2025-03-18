import string
from typing import Any, Iterable, Type, Union

import numpy as np
import pandas as pd

from geopandas_kml._utils.utils import formatter
from geopandas_kml.settings import NAMED_COLORS

HEX_PATTERN = string.hexdigits + "#"

Numeric = Union[int, float]

UniqueIterable = Union[tuple, list, np.ndarray, pd.Series]

HexCode = str
IterableHexCode = list[HexCode, ...]

IntRgb = tuple[int, int, int]
IterableIntRgb = list[IntRgb, ...]

ColorName = str
IterableColorName = list[ColorName, ...]

BACKWORD = "\nThe value you passed ---> kward: {kward}: type: {type}, value: {value}"


def dimensional_count(value: UniqueIterable) -> int:
    """
    ## Summary:
        Recursively determine the dimensionality of a list.
    Arguments:
        value (tuple | list | np.ndarray | pd.Series):
            The list to be measured.
    Returns:
        int: The dimensionality of the list.
            - 0: The value is not a list. (str, int, float, etc.)
            - 1: The value is a list.
            - 2: The value is a list of lists.
            - 3: The value is a list of lists of lists.
            - ...
    Examples:
        >>> dimensional_measurement(1)
        0
        >>> dimensional_measurement('a')
        0
        >>> dimensional_measurement([1, 2, 3])
        1
        >>> dimensional_measurement([[1, 2, 3], [4, 5, 6]])
        2
        >>> dimensional_measurement([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])
        3
    """
    if isinstance(value, UniqueIterable):
        try:
            value = value.tolist()
        except:
            try:
                value = value.tolist()
            except:
                pass
        return 1 + max(dimensional_count(item) for item in value) if value else 1
    else:
        return 0


def value_range_8bit(value: Numeric) -> bool:
    """
    ## Summary:
        Check if a value is within the 8-bit range.
    Arguments:
        value (int | float):
            The value to be measured.
    """
    return 0 <= value <= 255


def value_range_1(value: Numeric) -> bool:
    """
    ## Summary:
        Check if a value is within the 1-bit range.
    Arguments:
        value (int | float):
            The value to be measured.
    Returns:
        bool: True if the value is within the range, False otherwise.
    """
    return 0 <= value <= 1


def iterable_specific_type(value: UniqueIterable, type_: Type) -> bool:
    """
    ## Summary:
        Check if all items in a list are of a specific type.
    Arguments:
        value (tuple | list | np.ndarray | pd.Series):
            The list to be measured.
        type_ (Type):
            The type to check for.
    Returns:
        bool: True if all items are of the specified type, False otherwise.
    """
    np_types = {
        np.integer: int,
        np.int8: int,
        np.int16: int,
        np.int32: int,
        np.int64: int,
        np.floating: float,
        np.float16: float,
        np.float32: float,
        np.float64: float,
        np.str_: str,
    }
    dimensional = dimensional_count(value)
    if 0 < dimensional < 3:
        new_value = []
        for item in value:
            if type(item) in np_types:
                new_value.append(np_types.get(type(item))(item))
            else:
                new_value.append(item)
        return all(isinstance(item, type_) for item in new_value)
    return False


def hex_alpha_to_hex_abgr(value: HexCode, alpha: float) -> HexCode:
    """
    ## Summary:
        Convert a hexadecimal code to an ABGR code.
    Args:
        value (str): A hexadecimal code.
        alpha (float): An alpha value.
    Returns:
        str: An ABGR code. ABGR is a Google Earth KML color code.
    Raises:
        TypeError: If the value is not a string.
        ValueError: If the value is not a 6-digit hexadecimal code.
        TypeError: If the alpha value is not a float.
        ValueError: If the alpha value is not between 0 and 1.
    """
    if not isinstance(value, str):
        e = formatter(
            "The value must be a string."
            + BACKWORD.format(kward="value", type=type(value), value=repr(value))
        )
        raise TypeError(e)
    value = value.replace("#", "")
    is_hex = len(value) == 6 and all(c in HEX_PATTERN for c in value)
    if not is_hex:
        e = formatter(
            "The value must be a 6-digit hexadecimal code."
            + BACKWORD.format(kward="value", type=type(value), value=repr(value))
        )
        raise ValueError(e)
    if not isinstance(alpha, float):
        e = formatter(
            "The alpha value must be a float."
            + BACKWORD.format(kward="alpha", type=type(alpha), value=repr(alpha))
        )
        raise TypeError(e)
    elif not value_range_1(alpha):
        e = formatter(
            "The alpha value must be between 0 and 1."
            + BACKWORD.format(kward="alpha", type=type(alpha), value=repr(alpha))
        )
        raise ValueError(e)
    # Convert RGB to ABGR.
    idxs = [0, 2, 4]
    r, g, b = [value[idx : idx + 2] for idx in idxs]
    alpha = int(alpha * 255)
    return f"#{alpha:02x}{b}{g}{r}"


class IsRgb(object):
    def __init__(
        self,
        value: IntRgb | IterableIntRgb,
    ):
        """
        ## Summary:
            Check if the value is a valid RGB code.
            If RGB, the value is converted to hexadecimal and stored in `self.hex`.
        Args:
            value (tuple[int, int, int] | list[tuple[int, int, int]]):
                The value to be checked.
                value = (r, g, b) or [(r, g, b), ...]
                range is (0-255)
        """
        self.is_iterable = False
        self.is_valid = self._validation(value)
        self.hex = None
        if self.is_valid:
            # Convert tuple[r, g, b] to hex code.
            if self.is_iterable:
                self.hex = [self._to_hex_code(item) for item in value]
            else:
                self.hex = self._to_hex_code(value)

    def _validation(self, value: IntRgb | IterableIntRgb) -> bool:
        """
        ## Summary:
            Check if the value is a valid RGB code.
        Args:
            value (tuple[int, int, int] | list[tuple[int, int, int]]):
                The value to be checked.
                value = (r, g, b) or [(r, g, b), ...]
                range is (0-255)
        Returns:
            bool: True if the value is a valid RGB code, False otherwise.
        """
        dimension = dimensional_count(value)
        if dimension == 1:
            # True: tuple[int, int, int], False: other
            return (
                iterable_specific_type(value, int)
                and len(value) == 3
                and all(value_range_8bit(item) for item in value)
            )
        elif dimension == 2:
            self.is_iterable = True
            # True: list[tuple[int, int, int], ...], False: other
            return all(
                iterable_specific_type(item, int)
                and len(item) == 3
                and all(map(value_range_8bit, item))
                for item in value
            )
        return False

    def _to_hex_code(self, value: IntRgb) -> HexCode:
        return f"#{value[0]:02x}{value[1]:02x}{value[2]:02x}"


class IsHexCode(object):
    def __init__(
        self,
        value: HexCode | IterableHexCode,
    ):
        """
        ## Summary:
            Check if the value is a valid hexadecimal code.
            If hexadecimal, the value is stored in `self.hex`.
        Args:
            value (str | list[str]):
                The value to be checked.
                value = '#ffffff' or ['#ffffff ', ...]
                range is (0-9, a-f)
        """
        self.is_iterable = False
        self.is_valid = self._validation(value)
        self.hex = None
        if self.is_valid:
            self.hex = value

    def _validation(self, value: HexCode | IterableHexCode) -> bool:
        """
        ## Summary:
            Check if the value is a valid hexadecimal code.
        Args:
            value (str | list[str]):
                The value to be checked.
                value = '#ffffff' or ['#ffffff ', ...]
                range is (0-9, a-f)
        Returns:
            bool: True if the value is a valid hexadecimal code, False otherwise.
        """
        dimension = dimensional_count(value)
        if (dimension == 0) and isinstance(value, str):
            if len(value) == 7 or len(value) == 6:
                return all(c in HEX_PATTERN for c in value)
        elif dimension == 1:
            self.is_iterable = True
            # True: list[str, ...], False: other
            return all(
                isinstance(item, str) and (len(item) == 7 or len(item) == 6)
                for item in value
            )
        return False


class IsColorName(object):
    def __init__(
        self,
        value: ColorName | IterableColorName,
    ):
        """
        ## Summary:
            Check if the value is a valid color name.
            If a color name, the value is converted to hexadecimal and stored in `self.hex`.
        Args:
            value (str | list[str]):
                The value to be checked. value is {'tomato', 'teal', 'royalblue',
                  'firebrick', 'seagreen', 'dodgerblue', 'red', 'green', 'blue',
                  'gold', 'lime', 'cyan', 'maroon', 'olive', 'indigo', 'crimson',
                  'yellowgreen', 'navy', 'pink', 'skyblue', 'springgreen', 'magenta',
                  'yellow', 'brown', 'steelblue', 'violet', 'white', 'gray', 'black'
                }
        """
        self.is_iterable = False
        self.is_valid = self._validation(value)
        self.hex = None
        if self.is_valid:
            if self.is_iterable:
                self.hex = [NAMED_COLORS.get(item) for item in value]
            else:
                self.hex = NAMED_COLORS.get(value)

    def _validation(self, value: ColorName | IterableColorName) -> bool:
        """
        ## Summary:
            Check if the value is a valid color name.
        Args:
            value (str | list[str]):
                The value to be checked.
                value = 'red' or ['red', ...]
        Returns:
            bool: True if the value is a valid color name, False otherwise.
        """
        dimension = dimensional_count(value)
        if (dimension == 0) and isinstance(value, str):
            return value in NAMED_COLORS
        elif dimension == 1:
            self.is_iterable = True
            # True: list[str, ...], False: other
            return all(item in NAMED_COLORS for item in value)
        return False


class NormalizeColor(object):
    def __init__(
        self,
        value: ColorName
        | IterableColorName
        | IntRgb
        | IterableIntRgb
        | HexCode
        | IterableHexCode,
        alpha: float | Iterable[float] = 1.0,
    ):
        """
        ## Summary:
            Check if the value is a valid color code.
            If a valid color code, the value is converted to a KML color code
            and stored in `self.kml_hex`.
        Args:
            value (str | list[str] | tuple[int, int, int] | list[tuple[int, int, int]]):
                The value to be checked. value = 'red' or ['red', ...] or
                (r, g, b) or [(r, g, b), ...] or '#ffffff' or ['#ffffff', ...].
                name colors: {
                    'tomato', 'teal', 'royalblue', 'firebrick', 'seagreen',
                    'dodgerblue', 'red', 'green', 'blue', 'gold', 'lime',
                    'cyan', 'maroon', 'olive', 'indigo', 'crimson', 'yellowgreen',
                    'navy', 'pink', 'skyblue', 'springgreen', 'magenta', 'yellow',
                    'brown', 'steelblue', 'violet', 'white', 'gray', 'black'
                }
            alpha (float | list[float]):
                The alpha value.
                range is (0-1)
        """
        self.hex = None
        self.is_valid = False
        self.is_iterable = False
        self.is_valid = self._validation(value)
        self.kml_hex = None
        if self.is_valid:
            self.kml_hex = self._hex_to_kml_color(self.hex, alpha)

    def _validation(self, value: Any) -> bool:
        """
        ## Summary:
            Check if the value is a valid color code.
        """
        valid_cls = [IsColorName, IsRgb, IsHexCode]
        for cls in valid_cls:
            instance = cls(value)
            if instance.is_valid:
                self.hex = instance.hex
                self.is_iterable = instance.is_iterable
                return True
        return False

    def _hex_to_kml_color(
        self, hex_code: HexCode | IterableHexCode, alpha: float | Iterable[float]
    ) -> HexCode | Iterable[HexCode]:
        """
        ## Summary:
            Convert a hexadecimal code to a KML color code.
        Args:
            hex_code (str | list[str]):
                A hexadecimal code or a list of hexadecimal codes.
            alpha (float | list[float]):
                An alpha value or a list of alpha values.
        Returns:
            str | list[str]: A KML color code or a list of KML color codes.
        Raises:
            ValueError: If the length of the hex code and alpha value do not match.
            ValueError: If the alpha value is not a float or a list of floats.
        """
        is_iterable_alpha = isinstance(alpha, Iterable)
        if self.is_iterable:
            if is_iterable_alpha and len(hex_code) != len(alpha):
                e = formatter(
                    "The length of the hex code and alpha value must be the same."
                    + BACKWORD.format(
                        kward="hex_code, alpha",
                        type=f"{type(hex_code)}, {type(alpha)}",
                        value=f"{len(hex_code)}, {len(alpha)}",
                    )
                )
                raise ValueError(e)
            elif isinstance(alpha, float):
                alpha = [alpha] * len(hex_code)
            return [hex_alpha_to_hex_abgr(h, a) for h, a in zip(hex_code, alpha)]
        else:
            if isinstance(alpha, float):
                return hex_alpha_to_hex_abgr(hex_code, alpha)
            elif isinstance(alpha, Iterable):
                e = formatter(
                    "HexCode and alpha types do not match."
                    + BACKWORD.format(
                        kward="hex_code, alpha",
                        type=f"{type(hex_code)}, {type(alpha)}",
                        value=f"alpha len: {len(alpha)}",
                    )
                )
                raise ValueError(e)
            else:
                e = formatter(
                    "The alpha value must be a float or a list of floats."
                    + BACKWORD.format(
                        kward="alpha", type=type(alpha), value=repr(alpha)
                    )
                )
                raise ValueError(e)
