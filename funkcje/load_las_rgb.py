import laspy
import open3d as o3d
import numpy as np

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.vstack((x, y, z)).T
    print("Liczba punktów:", len(points))
    return points

las_file = r"79529_1503958_M-34-5-C-b-4-4-3-4.laz"
las = laspy.read(las_file)
points = read_las(las)

# Translacja do układu środka
translate_vector = las.header.min
points_translated = points - translate_vector
xt, yt, zt= points_translated[:, 0], points_translated[:, 1], points_translated[:, 2]

r = las.red / max(las.red)
g = las.green / max(las.green)
b = las.blue / max(las.blue)

# Wyodrębnianie punktów w zależności od klasy
def point_extraction_based_on_the_class(las, class_type):
    if class_type == 'buildings':
        print('Ekstrakcja punktów budynków')
        buildings_only = np.where(las.classification == 6)
        buildings_points = las.points[buildings_only]
        return buildings_points
    elif class_type == 'vegetation':
        print('Ekstrakcja punktów roślinności')
        vegetation_low = np.where(las.classification == 3)
        vegetation_medium = np.where(las.classification == 4)
        vegetation_high = np.where(las.classification == 5)
        vegetation = np.concatenate((vegetation_low, vegetation_medium,
        vegetation_high))
        vegetation_points = las.points[vegetation]
        return vegetation_points
    else:
        print('Ekstrakcja punktów gruntu')
        # Klasyfikacja 2 oznacza grunt
        ground_only = np.where(las.classification == 2)
        ground_points = las.points[ground_only]
        return ground_points

las_points = np.vstack((xt,yt,zt)).transpose()
las_colors = np.vstack((r,g,b)).transpose()

chmura_punktow = o3d.geometry.PointCloud()
chmura_punktow.points = o3d.utility.Vector3dVector(las_points)
chmura_punktow.colors = o3d.utility.Vector3dVector(las_colors)

o3d.visualization.draw_geometries_with_editing([chmura_punktow],window_name='Chmura punktów z kolorami')

# utworzenie nmt i nmpt z chmury punktów
