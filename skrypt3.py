import laspy
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.vstack((x, y, z)).T
    print("Liczba punktów:", len(points))
    return points

las_file1 = input("Podaj ścieżkę do pierwszej chmury punktów (.laz): ")
try:
    las1 = laspy.read(las_file1)
except Exception as e:
    print(f"Błąd przy wczytywaniu pliku: {e}")
    exit()

points1 = read_las(las1)

las_file2 = input("Podaj ścieżkę do drugiej chmury punktów (.laz): ")
try:
    las2 = laspy.read(las_file2)
except Exception as e:
    print(f"Błąd przy wczytywaniu pliku: {e}")
    exit()

points2 = read_las(las2)

output_difference = input("Podaj ścieżkę do wynikowego rastra różnicowego (.tif): ")
try:
    assert output_difference.endswith(".tif")
except AssertionError:
    print("Podano nieprawidłową ścieżkę do pliku")
    exit()

def laz_to_raster(points, cell_size):
    # find min and max values from point cloud
    min_x, min_y = points[:, 0].min(), points[:, 1].min()
    max_x, max_y = points[:, 0].max(), points[:, 1].max()

    # set number of rows and columns in raster
    n_cols = int(np.ceil((max_x - min_x) / cell_size))  
    n_rows = int(np.ceil((max_y - min_y) / cell_size))  

    lower_left = np.float64([min_x, min_y])

    # indices of pixels in raster
    i = np.uint16((points[:, 0] - lower_left[0]) / cell_size)
    j = np.uint16((points[:, 1] - lower_left[1]) / cell_size)

    pixels = pd.DataFrame()
    pixels["point_index"] = np.arange(points.shape[0])
    pixels["i"] = i
    pixels["j"] = j

    # function to process each group of points in a pixel
    def process_group(df: pd.DataFrame):
        points_in_pixel = df["point_index"]  
        zs = points[points_in_pixel, 2]  # z values
        return zs.max()  

    # group points by pixels and calculate max height in each pixel
    nmt = pixels.groupby(["i", "j"]).apply(process_group)

    raster = np.zeros((n_rows, n_cols)) 

    for (i, j), value in nmt.items():
        raster[n_rows - 1 - j, i] = value 

    crs = CRS.from_epsg(2180) 
    transform = from_origin(lower_left[0], lower_left[1] + (n_rows) * cell_size, cell_size, cell_size)

    return raster, crs, transform

cell_size = 1.0  

nmt_points1 = points1[las1.classification == 2]
nmpt_points1 = points1[np.isin(las1.classification, [2, 3, 4, 5, 6])]

print("Tworzenie rastrów NMT i NMPT dla chmur punktów...")
nmt1, _, _ = laz_to_raster(nmt_points1, cell_size)
nmpt1, crs, transform = laz_to_raster(nmpt_points1, cell_size)

nmt_points2 = points2[las2.classification == 2]
nmpt_points2 = points2[np.isin(las2.classification, [2, 3, 4, 5, 6])]

nmt2, _, _ = laz_to_raster(nmt_points2, cell_size)
nmpt2, _, _ = laz_to_raster(nmpt_points2, cell_size)

difference_raster = nmpt1 - nmpt2

# save difference raster to geotiff
with rasterio.open(output_difference, 'w', driver='GTiff', count=1, dtype=difference_raster.dtype, 
                   width=difference_raster.shape[1], height=difference_raster.shape[0], 
                   crs=crs, transform=transform, nodata=-9999) as dst:
    dst.write(difference_raster, 1)

print(f"Raster różnicowy zapisano do {output_difference}.")