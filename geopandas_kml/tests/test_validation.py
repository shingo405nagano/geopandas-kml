import numpy as np
import pandas as pd
import pytest

from geopandas_kml.validation import dimensional_count


@pytest.mark.parametrize(('value', 'expected'), [
    (0, 0),
    ([0, 0], 1),
    ([[0, 0], [0, 0]], 2),
    ([[[0, 0], [0, 0]], [[0, 0], [0, 0]]], 3),
    (np.array([0, 0]), 1),
    (np.array([[0], [0]]), 2),
    (np.array([[[0], [0]], [[0], [0]]]), 3),
    (pd.Series([0, 0]), 1)
])
def test_dimensional_count(value, expected):
    """Test the dimensional_count function."""
    assert dimensional_count(value) == expected


