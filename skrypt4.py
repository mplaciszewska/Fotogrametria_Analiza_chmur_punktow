import laspy
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.vstack((x, y, z)).T
    print("Liczba punktów:", len(points))
    return points

las_file = input("Podaj ścieżkę do pliku .laz: ")
try:
    las = laspy.read(las_file)
except Exception as e:
    print(f"Błąd przy wczytywaniu pliku: {e}")
    exit()

points = read_las(las)

points_buildings = points[np.where(las.classification == 6)]
points_ground = points[np.where(las.classification == 2)]

translate_vector = las.header.min
points_buildings_translated = points_buildings - translate_vector
points_ground_translated = points_ground - translate_vector

point_cloud = o3d.geometry.PointCloud()
point_cloud.points = o3d.utility.Vector3dVector(points_buildings_translated)

# clustering for buildings
labels_buildings = np.array(point_cloud.cluster_dbscan(eps=3.5, min_points=50))
max_label_buildings = labels_buildings.max()
print(f"Utworzono {max_label_buildings + 1} klastrów.")

colors_buildings = np.random.rand(max_label_buildings + 1, 3) 
point_colors_buildings = np.zeros((labels_buildings.shape[0], 3))

for i in range(max_label_buildings + 1):
    point_colors_buildings[labels_buildings == i] = colors_buildings[i]

point_cloud.colors = o3d.utility.Vector3dVector(point_colors_buildings)

point_cloud_ground = o3d.geometry.PointCloud()
point_cloud_ground.points = o3d.utility.Vector3dVector(points_ground_translated)
point_colors_ground = np.full((points_ground_translated.shape[0], 3), [0.8, 0.5, 0.2])
point_cloud_ground.colors = o3d.utility.Vector3dVector(point_colors_ground)

# combine point clouds
point_cloud = point_cloud + point_cloud_ground
o3d.visualization.draw_geometries([point_cloud], window_name="Klasteryzacja budynków")

