from dataclasses import dataclass
import random
import string
from typing import List

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely


@dataclass
class DummyGeometry:
    # point geometries
    POINT_OBJ: shapely.Point = shapely.Point(140.0, 40.0)
    POINT_OBJ2: shapely.Point = shapely.Point(140.1, 40.1)
    MULTI_POINT_OBJ: shapely.MultiPoint = shapely.MultiPoint([POINT_OBJ, POINT_OBJ2])
    POINT_OBJ_3D: shapely.Point = shapely.Point(140.0, 40.0, 100.0)
    POINT_OBJ_3D2: shapely.Point = shapely.Point(140.1, 40.1, 100.0)
    MULTI_POINT_OBJ_3D: shapely.MultiPoint = shapely.MultiPoint(
        [POINT_OBJ_3D, POINT_OBJ_3D2]
    )
    # line geometries
    LINESTRING_OBJ: shapely.LineString = shapely.LineString(
        [(140.0, 40.0), (141.0, 40.0)]
    )
    LINESTRING_OBJ2: shapely.LineString = shapely.LineString(
        [(140.1, 40.1), (140.2, 40.1)]
    )
    MULTI_LINESTRING_OBJ: shapely.MultiLineString = shapely.MultiLineString(
        [LINESTRING_OBJ, LINESTRING_OBJ2]
    )
    LINESTRING_OBJ_3D: shapely.LineString = shapely.LineString(
        [(140.0, 40.0, 100.0), (141.0, 40.0, 100.0)]
    )
    LINESTRING_OBJ_3D2: shapely.LineString = shapely.LineString(
        [(140.1, 40.1, 100.0), (140.2, 40.1, 100.0)]
    )
    MULTI_LINESTRING_OBJ_3D: shapely.MultiLineString = shapely.MultiLineString(
        [LINESTRING_OBJ_3D, LINESTRING_OBJ_3D2]
    )
    # polygon geometries
    POLYGON_OBJ: shapely.Polygon = shapely.Polygon(
        shell=[
            (139.00, 38.5),
            (139.00, 39.5),
            (140.00, 39.5),
            (140.00, 38.5),
            (139.00, 38.5),
        ]
    )
    POLYGON_OBJ2: shapely.Polygon = shapely.Polygon(
        shell=[
            (140.0, 40.0),
            (141.0, 40.0),
            (141.0, 41.0),
            (140.0, 41.0),
            (140.0, 40.0),
        ],
        holes=[
            [(140.1, 40.1), (140.2, 40.1), (140.2, 40.2), (140.1, 40.2), (140.1, 40.1)],
            [(140.8, 40.8), (140.9, 40.8), (140.9, 40.9), (140.8, 40.9), (140.8, 40.8)],
            [(140.5, 40.5), (140.6, 40.5), (140.6, 40.6), (140.5, 40.6), (140.5, 40.5)],
            [(140.3, 40.3), (140.4, 40.3), (140.4, 40.4), (140.3, 40.4), (140.3, 40.3)],
        ],
    )
    POLYGON_OBJ3: shapely.Polygon = shapely.Polygon(
        shell=[
            (141.5, 39.5),
            (141.5, 40.5),
            (142.5, 40.5),
            (142.5, 39.5),
            (141.5, 39.5),
        ],
        holes=[
            [(141.6, 39.6), (141.6, 40.4), (142.4, 40.4), (142.4, 39.6), (141.6, 39.6)],
            [(141.7, 39.7), (141.7, 40.3), (142.3, 40.3), (142.3, 39.7), (141.7, 39.7)],
        ],
    )
    MULTI_POLYGON_OBJ: shapely.MultiPolygon = shapely.MultiPolygon(
        [POLYGON_OBJ2, POLYGON_OBJ, POLYGON_OBJ3]
    )
    # linear ring geometries
    LINEAR_RING_OBJ: shapely.LinearRing = shapely.LinearRing(
        [(139.00, 38.5), (139.00, 39.5), (140.00, 39.5), (140.00, 38.5), (139.00, 38.5)]
    )
    # collection geometries
    GEOMETRY_COLLECTION_OBJ: shapely.GeometryCollection = shapely.GeometryCollection(
        [POINT_OBJ, LINESTRING_OBJ, POLYGON_OBJ]
    )


class DummyData(object):
    def __init__(self, lon: float = 140.464668, lat: float = 40.607567):
        self.lon = lon
        self.lat = lat

    def get_ids(self, size: int) -> List[str]:
        alphabet = string.ascii_uppercase
        ids = []
        for _ in range(size):
            ids.append("".join([random.choice(alphabet) for _ in range(5)]))
        return ids

    def get_codes(self, size: int) -> List[str]:
        alphabets = string.ascii_uppercase[:5]
        return [random.choice(alphabets) for _ in range(size)]

    def get_gender(self, size: int) -> List[str]:
        lst = ["man", "woman"]
        return [random.choice(lst) for _ in range(size)]

    def get_ages(self, size: int) -> np.ndarray:
        return np.random.normal(35, 10, size).astype(int)

    def get_height(self, size: int) -> np.ndarray:
        return np.random.normal(165, 10, size).round(1)

    def get_weight(self, size: int) -> np.ndarray:
        return np.random.normal(60, 10, size).round(1)

    def get_dataframe(self, size: int) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "id": self.get_ids(size),
                "code": self.get_codes(size),
                "gender": self.get_gender(size),
                "age": self.get_ages(size),
                "height": self.get_height(size),
                "weight": self.get_weight(size),
            }
        )

    def get_lons(self, size: int, scale: float = 0.1) -> np.ndarray:
        return np.random.normal(self.lon, scale, size)

    def get_lats(self, size: int, scale: float = 0.1) -> np.ndarray:
        return np.random.normal(self.lat, scale, size)

    def point_geodataframe(
        self, size: int = 20, scale: float = 0.1
    ) -> gpd.GeoDataFrame:
        lons = self.get_lons(size, scale)
        lats = self.get_lats(size, scale)
        gdf = gpd.GeoDataFrame(
            data=self.get_dataframe(size),
            geometry=gpd.points_from_xy(lons, lats, crs="EPSG:4326"),
        )
        return gdf

    def line_geodataframe(self, size: int = 20, scale: float = 0.1) -> gpd.GeoDataFrame:
        shift = scale * 0.1
        lons = self.get_lons(size, scale)
        lons2 = lons + shift
        lats = self.get_lats(size, scale)
        lats2 = lats + shift
        lines = []
        for lon1, lon2, lat1, lat2 in zip(lons, lons2, lats, lats2):
            lines.append(shapely.geometry.LineString([(lon1, lat1), (lon2, lat2)]))
        gdf = gpd.GeoDataFrame(
            data=self.get_dataframe(size), geometry=lines, crs="EPSG:4326"
        )
        return gdf

    def polygon_geodataframe(
        self, size: int = 20, scale: float = 0.1
    ) -> gpd.GeoDataFrame:
        pnt_gdf = self.point_geodataframe(size, scale)
        polys = [geom.envelope for geom in pnt_gdf.geometry.buffer(scale * 0.1)]
        return gpd.GeoDataFrame(
            data=pnt_gdf.drop(columns="geometry"), geometry=polys, crs="EPSG:4326"
        )

    def multi_point_geodataframe(
        self, size: int = 20, scale: float = 0.1, shift: float = 0.5
    ) -> gpd.GeoDataFrame:
        lons = self.get_lons(size, scale)
        lons2 = lons + shift
        lats = self.get_lats(size, scale)
        lats2 = lats
        points = []
        for lon1, lon2, lat1, lat2 in zip(lons, lons2, lats, lats2):
            mpnt = shapely.geometry.MultiPoint([(lon1, lat1), (lon2, lat2)])
            points.append(mpnt)
        gdf = gpd.GeoDataFrame(
            data=self.get_dataframe(size), geometry=points, crs="EPSG:4326"
        )
        return gdf

    def multi_line_geodataframe(
        self, size: int = 20, scale: float = 0.1, shift: float = 0.5
    ) -> gpd.GeoDataFrame:
        line_gdf = self.line_geodataframe(size, scale)
        lines1 = line_gdf.geometry.to_list()
        lines2 = [
            shapely.affinity.translate(line, xoff=shift, yoff=0) for line in lines1
        ]
        mlines = [
            shapely.geometry.MultiLineString([line1, line2])
            for line1, line2 in zip(lines1, lines2)
        ]
        return gpd.GeoDataFrame(
            data=line_gdf.drop(columns="geometry"), geometry=mlines, crs="EPSG:4326"
        )

    def multi_polygon_geodataframe(
        self, size: int = 20, scale: float = 0.1, shift: float = 0.5
    ) -> gpd.GeoDataFrame:
        poly_gdf = self.polygon_geodataframe(size, scale)
        polys1 = poly_gdf.geometry.to_list()
        polys2 = [
            shapely.affinity.translate(poly, xoff=shift, yoff=0) for poly in polys1
        ]
        mpolygons = [
            shapely.geometry.MultiPolygon([poly1, poly2])
            for poly1, poly2 in zip(polys1, polys2)
        ]
        return gpd.GeoDataFrame(
            data=poly_gdf.drop(columns="geometry"), geometry=mpolygons, crs="EPSG:4326"
        )


if __name__ == "__main__":
    dummy_geom = DummyGeometry()
    print(dummy_geom.MULTI_POINT_OBJ)
    dummy_data = DummyData()

    # pnt_gdf = dummy_data.point_geodataframe()
    # mpnt_gdf = dummy_data.multi_point_geodataframe()
    # line_gdf = dummy_data.line_geodataframe()
    # mline_gdf = dummy_data.multi_line_geodataframe()
    # poly_gdf = dummy_data.polygon_geodataframe()
    # mpoly_gdf = dummy_data.multi_polygon_geodataframe()
    # df.to_file('line_data.geojson', driver='GeoJSON')
