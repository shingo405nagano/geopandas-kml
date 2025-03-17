import string
from typing import Any
from typing import Iterable
from typing import Optional
from typing import Type
from typing import Union

import fastkml
import fastkml.geometry
import geopandas
import numpy as np
import pandas as pd
import pydantic
import pygeoif
import shapely
from shapely.geometry.base import BaseGeometry as ShapelyBaseGeometry

from geopandas_kml.utils import BACK_WORD
from geopandas_kml.utils import formatter

FastKmlGeometry = Union[
    fastkml.geometry.Point,
    fastkml.geometry.LineString,
    fastkml.geometry.LinearRing,
    fastkml.geometry.Polygon,
    fastkml.geometry.MultiGeometry,
]

HEX_PATTERN = string.hexdigits + "#"

Numeric = Union[int, float]

UniqueIterable = Union[tuple, list, np.ndarray, pd.Series]

HexCode = str
IterableHexCode = list[HexCode, ...]

IntRgb = tuple[int, int, int]
IterableIntRgb = list[IntRgb, ...]

ColorName = str
IterableColorName = list[ColorName, ...]

_ALTIMODES = "'clamp_to_ground', 'relative_to_ground', 'absolute'."


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


class ValidateGeometry(pydantic.BaseModel):
    """
    ## Summary:
        MakeGeometry is a class that represents a geometry element in the KML file.

    Args:
        geometry(shapely.geometry.base.BaseGeometry):
            The geometry object is a shapely geometry object.
            - shapely.geometry.Point
            - shapely.geometry.LineString
            - shapely.geometry.LinearRing
            - shapely.geometry.Polygon
            - shapely.geometry.MultiPoint
            - shapely.geometry.MultiLineString
            - shapely.geometry.MultiPolygon

        extrude(bool):
            Specifies whether to connect the geometry to the ground.
            To extrude a geometry, the altitude mode must be either
            'relativeToGround' or 'absolute'.

        tessellate(bool):
            Specifies whether to allow the LineString to follow the terrain.
            To enable tessellation, the 'altitude' mode must be 'clampToGround'.
            Ignored except for LineString.

        altitude_mode(str):
            Specifies how the geometry is placed in relation to the earth's surface.
            - 'crampToGround': Indicates to ignore an altitude specification.
            - 'relativeToGround': Sets the altitude of the element relative to the
                                  actual ground elevation of a particular location.
            - 'absolute': Sets the altitude of the coordinate relative to sea level,
                          regardless of the actual elevation of the terrain beneath
                          the element.
    """

    geometry: pygeoif.geometry.Geometry
    extrude: bool
    tessellate: bool
    altitude_mode: fastkml.geometry.AltitudeMode
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    @pydantic.field_validator("geometry", mode="before")
    @classmethod
    def _validate_geometry(
        cls, geometry: ShapelyBaseGeometry
    ) -> pygeoif.geometry.Geometry:
        """
        ## Summary:
            Validate the geometry.

        Args:
            geometry(shapely.geometry.base.BaseGeometry):
                The geometry object is a shapely geometry object.
                - shapely.geometry.Point
                - shapely.geometry.LineString
                - shapely.geometry.LinearRing
                - shapely.geometry.Polygon
                - shapely.geometry.MultiPoint
                - shapely.geometry.MultiLineString
                - shapely.geometry.MultiPolygon

        Returns:
            (pygeoif.geometry.Geometry):
                The geometry object is a pygeoif geometry object.
        """
        if not isinstance(geometry, ShapelyBaseGeometry):
            msg = "``geometry`` must be a shapely geometry."
            msg += BACK_WORD.format(
                kward="geometry", type=type(geometry), value=geometry
            )
            raise ValueError(formatter(msg))
        if not shapely.is_valid(geometry):
            geometry = shapely.make_valid(geometry)
        return pygeoif.shape(geometry)

    @pydantic.field_validator("extrude", "tessellate", mode="before")
    @classmethod
    def _validate_bool(cls, value: bool) -> bool:
        """
        ## Summary:
            Validate the boolean value.

        Args:
            value(bool):
                The boolean value to validate.

        Returns:
            (bool):
                The validated boolean value.
        """
        if not isinstance(value, bool):
            msg = "value must be a boolean."
            msg += BACK_WORD.format(kward="value", type=type(value), value=value)
            try:
                if int(value) in [0, 1]:
                    return bool(value)
                raise ValueError
            except Exception as e:
                raise ValueError(formatter(msg) + str(e)) from e
        return value

    @pydantic.field_validator("altitude_mode", mode="before")
    @classmethod
    def _validate_altitude_mode(cls, value: str) -> str:
        """
        ## Summary:
            Validate the altitude mode.

        Args:
            value(str):
                The altitude mode.
                - 'clamp_to_ground'
                - 'relative_to_ground'
                - 'absolute'

        Returns:
            (str):
                The altitude mode.
        """
        if not isinstance(value, str):
            msg = "``altitude_mode`` must be a string. Must be one of: " + _ALTIMODES
            msg += BACK_WORD.format(
                kward="altitude_mode", type=type(value), value=value
            )
            raise ValueError(formatter(msg))
        value = value.lower()
        members = fastkml.geometry.AltitudeMode.__members__
        if value not in members:
            msg = "``altitude_mode`` must be one of:" + _ALTIMODES
            msg += BACK_WORD.format(
                kward="altitude_mode", type=type(value), value=value
            )
            raise ValueError(formatter(msg))
        return members[value]

    def kml_geometry(self) -> FastKmlGeometry:
        """
        ## Summary:
            This function creates a KML geometry object.

        Returns:
            (fastkml.geometry.Geometry):
        Examples:
            >>> from geopandas_kml.utils.geometries import MakeGeometry
            >>> from shapely.geometry import Point
            >>> maked_geom = MakeGeometry(
            ...     geometry=Point(140.0, 40.0),
            ...     extrude=True,
            ...     tessellate=True,
            ...     altitude_mode="clamp_to_ground",
            ... )
            >>> print(maked_geom.kml_geometry())
            <kml:Point xmlns:kml="http://www.opengis.net/kml/2.2">
                <kml:extrude>1</kml:extrude>
                <kml:altitudeMode>clampToGround</kml:altitudeMode>
                <kml:coordinates>140.0,40.0</kml:coordinates>
            </kml:Point>
        """
        return fastkml.geometry.create_kml_geometry(**self.__dict__)


class ValidateGeoSeries(pydantic.BaseModel):
    """
    ## Summary:
        ValidateGeoSeries is a class for validating whether a ``geoseries`` is
        the intended data.

    Args:
        geoseries(geopandas.GeoSeries | Iterable[shapely.geometry.base.BaseGeometry]):
            The geoseries object is a geopandas GeoSeries object or an iterable
            of shapely geometries.
    """

    geoseries: geopandas.GeoSeries | Iterable[shapely.geometry.base.BaseGeometry]
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    @pydantic.field_validator("geoseries", mode="before")
    @classmethod
    def _validate_geometry(cls, geoseries):
        """
        ## Summary:
            Validate the geoseries.

        Args:
            geoseries(geopandas.GeoSeries | Iterable[shapely.geometry.base.BaseGeometry]):
                The geoseries object is a geopandas GeoSeries object or an iterable
                of shapely geometries.

        Returns:
            (geopandas.GeoSeries | Iterable[shapely.geometry.base.BaseGeometry]):
                The validated geoseries object.
        """
        if not isinstance(geoseries, str) and isinstance(geoseries, Iterable):
            if not iterable_specific_type(
                geoseries, shapely.geometry.base.BaseGeometry
            ):
                msg = (
                    "``geoseries`` must be a `geopandas.GeoSeries` or an iterable of "
                    "shapely geometries."
                )
                types = set([type(geo) for geo in geoseries])
                msg += BACK_WORD.format(
                    kward="geoseries", type=type(geoseries), value=types
                )
                raise ValueError(formatter(msg))
            else:
                return geoseries
        else:
            msg = (
                "``geoseries`` must be a `geopandas.GeoSeries` or an iterable "
                "of shapely geometries."
            )
            msg += BACK_WORD.format(
                kward="geoseries", type=type(geoseries), value=geoseries
            )
            raise ValueError(formatter(msg))


class ValidateData(pydantic.BaseModel):
    """
    ## Summary:
        ValidateData is a class for validating the data element in the KML file.

    Args:
        name (str):
            The name of the data element.

        value (str):
            The value of the data element.

        display_name (Optional[str]):
            The display name of the data element. If ``display_name`` is
            present, then The ``display_name`` will appear on the screen.

    Example:
        >>> data = MakeData(
        ...     name="pref", value="Aomori", display_name="Prefecture")
        >>> data_elem = data.kml_extended_data()
        >>> print(data_elem)
        <kml:Data xmlns:kml="http://www.opengis.net/kml/2.2" name="pref">
            <kml:displayName>Prefecture</kml:displayName>
            <kml:value>Aomori</kml:value>
        </kml:Data>
    """

    name: str
    value: str
    display_name: Optional[str] = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def convert_fields(cls, input_data: dict[str, Any]) -> str:
        """
        ## Summary:
            Convert the fields to a string.

        Args:
            (dict[str, Any]):
                The input data to be converted.

        Returns:
            (str):
                The parsed data.
        """
        try:
            parsed_data = {
                key: str(val) if val is not None else None
                for key, val in input_data.items()
            }
        except Exception:
            msg = "Failed to parse the fields."
            msg += BACK_WORD.format(
                kward="input_data", type=type(input_data), value=input_data
            )
            raise ValueError(formatter(msg))
        return parsed_data

    def kml_extended_data(self) -> fastkml.data.Data:
        """
        ## Summary:
            Return the extended data for the KML file.

        Returns:
            (fastkml.data.Data):
                The extended data for the KML file.
        Examples:
            >>> data = MakeData(
            ...     name="pref", value="Aomori", display_name="Prefecture")
            >>> data_elem = data.kml_extended_data()
            >>> print(data_elem)
            <kml:Data xmlns:kml="http://www.opengis.net/kml/2.2" name="pref">
                <kml:displayName>Prefecture</kml:displayName>
                <kml:value>Aomori</kml:value>
            </kml:Data>
        """
        return fastkml.data.Data(**self.__dict__)
