"""
geopandas_kml
"""

import warnings

import pandas as pd
from pandas.util._decorators import doc
from pandas.util._exceptions import find_stack_level


class Cached:
    """
    Custom property-like object. A descriptor for caching accessors.
    Args:
        name(str): Namespace that will be accessed under, e.g. ``df.foo``.
        accessor(cls): Class with the extension methods.
    Notes:
        The class's __init__ method assumes that one of `Series`,
        `DataFrame` or `Index` as the single argument `data`.
    """

    def __init__(self, name: str, accessor) -> None:
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            return self._accessor
        accessor_obj = self._accessor(obj)
        object.__setattr__(obj, self._name, accessor_obj)
        return accessor_obj


@doc(klass="", others="")
def _register_accessor(name: str, cls):
    def decorator(accessor):
        if hasattr(cls, name):
            warnings.warn(
                f"registration of accessor {repr(accessor)} under name "
                f"{repr(name)} for type {repr(cls)} is overriding a preexisting "
                f"attribute with the same name.",
                UserWarning,
                stacklevel=find_stack_level(),
            )
        setattr(cls, name, Cached(name, accessor))
        cls._accessors.add(name)
        return accessor

    return decorator


@doc(_register_accessor, klass="DataFrame")
def register_dataframe_accessor(name: str):
    return _register_accessor(name, pd.DataFrame)


@register_dataframe_accessor("kml")
class Accsess(object):
    def __init__(self, obj):
        self._data = obj
        self._index = obj.index
        self._name = None

    def _printer_(self):
        """
        Return the data.
        """
        print(self._data)
