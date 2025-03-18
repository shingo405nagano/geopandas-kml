from geopandas import GeoDataFrame


class CustomGeoDataFrame(GeoDataFrame):
    @property
    def _constructor(self):
        return CustomGeoDataFrame

    def to_kml(self):
        """
        Convert the GeoDataFrame to a KML file.
        """
        print(self)


def create_geodataframe(*args, **kwargs):
    return CustomGeoDataFrame(*args, **kwargs)
