import os
import geopandas as gpd

# Enable SHX recovery for incomplete shapefiles
os.environ["SHAPE_RESTORE_SHX"] = "YES"


def load_projected_shapefile(
    shapefile_path: str,
    target_epsg: int = 32654,
    scale_factor: float = 0.001,
) -> gpd.GeoDataFrame:
    """Loads a GIS shapefile, ensures CRS, reprojects to target EPSG, and scales coordinates."""
    gdf = gpd.read_file(shapefile_path)
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    gdf = gdf.to_crs(epsg=target_epsg)
    if scale_factor != 1.0:
        gdf.geometry = gdf.geometry.scale(
            xfact=scale_factor, yfact=scale_factor, origin=(0, 0)
        )
    return gdf
