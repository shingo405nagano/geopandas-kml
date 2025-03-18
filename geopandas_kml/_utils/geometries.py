"""
Docstring:

This module contains functions to convert geometries between different formats.
"""

from typing import Iterable
from typing import Optional
from typing import Union

import fastkml
import fastkml.geometry
import geopandas
import numpy as np
import pydantic
import pygeoif
import shapely
from shapely.geometry.base import BaseGeometry as ShapelyBaseGeometry

from geopandas_kml._utils.utils import BACK_WORD
from geopandas_kml._utils.utils import formatter
from geopandas_kml._utils.validation import iterable_specific_type
from geopandas_kml._utils.validation import Numeric
from geopandas_kml._utils.validation import value_range_1

FastKmlGeometry = Union[
    fastkml.geometry.Point,
    fastkml.geometry.LineString,
    fastkml.geometry.LinearRing,
    fastkml.geometry.Polygon,
    fastkml.geometry.MultiGeometry,
]

_ALTIMODES = "'clamp_to_ground', 'relative_to_ground', 'absolute'."


def geoseries_to_kml(
    geoseries: geopandas.GeoSeries | Iterable[shapely.geometry.base.BaseGeometry],
    extrude: bool | Iterable[bool] = True,
    tessellate: bool | Iterable[bool] = True,
    altitude_mode: str | Iterable[str] = "clamp_to_ground",
) -> list[FastKmlGeometry]:
    """
    ## Summary:
    """
    # validate geoseries
    if not isinstance(geoseries, str):
        if not iterable_specific_type(geoseries, shapely.geometry.base.BaseGeometry):
            msg = (
                "``geoseries`` must be a `geopandas.GeoSeries` or an iterable of "
                "shapely geometries."
            )
            msg += BACK_WORD.format(
                kward="geoseries", type=type(geoseries), value=geoseries[:5]
            )
            raise ValueError(formatter(msg))
        else:
            length = len(geoseries)
    else:
        msg = (
            "``geoseries`` must be a `geopandas.GeoSeries` or an iterable "
            "of shapely geometries."
        )
        msg += BACK_WORD.format(
            kward="geoseries", type=type(geoseries), value=geoseries
        )
        raise ValueError(formatter(msg))

    # validate extrude
    if isinstance(extrude, bool) or isinstance(extrude, Numeric):
        # If ``extrude`` has one value, apply to all ``geoseries``
        if isinstance(extrude, bool):
            extrude = [extrude] * length
        elif value_range_1(extrude):
            extrude = [extrude] * length
        else:
            msg = "``extrude`` must be a boolean or an iterable of booleans."
            msg += BACK_WORD.format(kward="extrude", type=type(extrude), value=extrude)
            raise ValueError(formatter(msg))
    # If ``extrude`` has multiple values, check the length.
    elif iterable_specific_type(extrude, bool):
        if length != len(extrude):
            msg = (
                "The length of ``extrude`` must be the same as the length of "
                "``geoseries``."
            )
            msg += BACK_WORD.format(
                kward="extrude", type=type(extrude), value=len(extrude)
            )
            raise ValueError(formatter(msg))
    elif iterable_specific_type(extrude, Numeric):
        if not all([value_range_1(value) for value in extrude]):
            # If the values are not in the range of 0 and 1, raise an error.
            msg = "The value must be in the range of 0 and 1."
            msg += BACK_WORD.format(
                kward="extrude",
                type=type(extrude),
                value=f"\nMax: {np.max(extrude)}, Min: {np.min(extrude)}",
            )
            raise ValueError(formatter(msg))
        elif length != len(extrude):
            msg = (
                "The length of ``extrude`` must be the same as the length of "
                "``geoseries``."
            )
            msg += BACK_WORD.format(
                kward="extrude", type=type(extrude), value=len(extrude)
            )
            raise ValueError(formatter(msg))
    else:
        msg = "``extrude`` must be a boolean or an iterable of booleans."
        msg += BACK_WORD.format(kward="extrude", type=type(extrude), value=extrude)
        raise ValueError(formatter(msg))
    # validate tessellate
    if isinstance(tessellate, bool) or isinstance(tessellate, Numeric):
        # If ``tessellate`` has one value, apply to all ``geoseries``
        if isinstance(tessellate, bool):
            tessellate = [tessellate] * length
        elif value_range_1(tessellate):
            tessellate = [tessellate] * length
        else:
            msg = "``tessellate`` must be a boolean or an iterable of booleans."
            msg += BACK_WORD.format(
                kward="tessellate", type=type(tessellate), value=tessellate
            )
            raise ValueError(formatter(msg))
    # If ``tessellate`` has multiple values, check the length.
    elif iterable_specific_type(tessellate, bool):
        if length != len(tessellate):
            msg = (
                "The length of ``tessellate`` must be the same as the length of "
                "``geoseries``."
            )
            msg += BACK_WORD.format(
                kward="tessellate", type=type(tessellate), value=len(tessellate)
            )
            raise ValueError(formatter(msg))
    elif iterable_specific_type(tessellate, Numeric):
        if not all([value_range_1(value) for value in tessellate]):
            # If the values are not in the range of 0 and 1, raise an error.
            msg = "The value must be in the range of 0 and 1."
            msg += BACK_WORD.format(
                kward="tessellate",
                type=type(tessellate),
                value=f"\nMax: {np.max(tessellate)}, Min: {np.min(tessellate)}",
            )
            raise ValueError(formatter(msg))
        elif length != len(tessellate):
            msg = (
                "The length of ``tessellate`` must be the same as the length of "
                "``geoseries``."
            )
            msg += BACK_WORD.format(
                kward="tessellate", type=type(tessellate), value=len(tessellate)
            )
            raise ValueError(formatter(msg))
    else:
        msg = "``tessellate`` must be a boolean or an iterable of booleans."
        msg += BACK_WORD.format(
            kward="tessellate", type=type(tessellate), value=tessellate
        )
        raise ValueError(formatter(msg))
