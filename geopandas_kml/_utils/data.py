from typing import Any, Iterable, Optional

import fastkml
import pandas as pd
import pydantic

from geopandas_kml._utils.utils import BACK_WORD
from geopandas_kml._utils.utils import formatter


def dataframe_to_extended_data_elements(
    dataframe: pd.DataFrame, display_names: list[str] = None
) -> dict[int, fastkml.data.ExtendedData]:
    """
    ## Summary:
        Convert the DataFrame to a list of extended data elements.

    Args:
        dataframe (pd.DataFrame):
            The DataFrame to be converted.

        display_names (list[str]):
            The ``display_names`` length must be the same as the number
            of columns in the DataFrame.

    Returns:
        (dict[int, fastkml.data.ExtendedData]):
            The dictionary of extended data elements. The key is the index
            of the DataFrame.

    Examples:
        >>> import pandas as pd
        >>> from geopandas_kml.utils.data import dataframe_to_extended_data_elements
        >>> df = pd.DataFrame({
        ...    "pref": ["Aomori", "Iwate"],
        ...    "city": ["Aomori", "Morioka"]
        ... })
        >>> display_names = ["Prefecture", "City"]
        >>> extended_data_list = dataframe_to_extended_data_elements(
        ...     dataframe=df, display_names=display_names)
        ... print(extended_data_list[0])
        <kml:ExtendedData xmlns:kml="http://www.opengis.net/kml/2.2">
            <kml:Data name="pref">
                <kml:displayName>Prefecture</kml:displayName>
                <kml:value>Aomori</kml:value>
            </kml:Data>
            <kml:Data name="city">
                <kml:displayName>City</kml:displayName>
                <kml:value>Aomori</kml:value>
            </kml:Data>
        </kml:ExtendedData>
    """
    if (display_names is not None) & isinstance(display_names, Iterable):
        if len(display_names) != len(dataframe.columns):
            msg = (
                "The length of the fields must be the same as the number of "
                "columns in the DataFrame."
            )
            msg += BACK_WORD.format(
                kward="display_names", type=type(display_names), value=display_names
            )
            raise ValueError(formatter(msg))
    else:
        display_names = [None] * len(dataframe.columns)

    elements = {}
    for i, row in enumerate(dataframe.to_dict(orient="records")):
        data_list = []
        for (name, value), display_name in zip(row.items(), display_names):
            data = MakeData(name=name, value=value, display_name=display_name)
            data_list.append(data.kml_extended_data())
        extended_data = fastkml.data.ExtendedData()
        extended_data.elements = data_list
        elements[i] = extended_data
    return elements
