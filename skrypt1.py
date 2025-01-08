import laspy
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.vstack((x, y, z)).T
    print("Liczba punktów:", len(points))
    return points

def visualize_point_cloud_by_class(x, y, z, classification):
    print("Wizualizacja chmury punktów...")
    las_points = np.vstack((x, y, z)).transpose()
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(las_points)
    colors = np.array([color_palette.get(cls, [1.0, 1.0, 1.0]) for cls in classification])
    point_cloud.colors = o3d.utility.Vector3dVector(colors)

    o3d.visualization.draw_geometries([point_cloud], window_name='Chmura punktów')
    

def calc_number_of_points_in_classes(las):
    classes = np.unique(las.classification)
    for cls in classes:
        quantity_by_class[cls] = len(np.where(las.classification == cls)[0])

las_file = input("Podaj ścieżkę do pliku .laz: ")

# Wczytanie pliku LAS
try:
    las = laspy.read(las_file)
except Exception as e:
    print(f"Błąd przy wczytywaniu pliku: {e}")
    exit()
points = read_las(las)

allowed_classes = [0,1,2,3,4,5,6,9]

where_not_noise = np.isin(las["classification"], allowed_classes)
points = points[where_not_noise]
classification = las["classification"][where_not_noise]

translate_vector = las.header.min
points_translated = points - translate_vector
xt, yt, zt= points_translated[:, 0], points_translated[:, 1], points_translated[:, 2]



# classes dict
classes_ASPRS = {
    0: 'never classified',
    1: 'unclassified',
    2: 'ground',
    3: 'vegetation low',
    4: 'vegetation medium',
    5: 'vegetation high',
    6: 'buildings',
    7: 'low point(noise)',
    8: 'model key-point (masspoint)',
    9: 'water',
    10: 'reserved for ASPRS Definition',
    11: 'reserved for ASPRS Definition',
    12: 'overlap points'
}

color_palette = {
    0: [0.5, 0.5, 0.5],  # Szary
    1: [0.8, 0.8, 0.8],  # Jasnoszary
    2: [0.6, 0.4, 0.2],  # Brązowy (ziemia)
    3: [0.0, 0.4, 0.0],  # Ciemnozielony (niskie rośliny)
    4: [0.0, 0.8, 0.0],  # Zielony (średnie rośliny)
    5: [0.0, 1.0, 0.0],  # Jasnozielony (wysokie rośliny)
    6: [1.0, 0.0, 0.0],  # Czerwony (budynki)
    7: [1.0, 1.0, 0.0],  # Żółty (szum)
    8: [0.0, 1.0, 1.0],  # Turkusowy (punkty kluczowe)
    9: [0.0, 0.0, 1.0],  # Niebieski (woda)
    10: [0.3, 0.3, 0.3], # Rezerwacja
    11: [0.4, 0.4, 0.4], # Rezerwacja
    12: [1.0, 0.5, 0.0], # Pomarańczowy (punkty nakładające się)
}
quantity_by_class = {}

calc_number_of_points_in_classes(las)

# bar chart with number of points in classes
fig, ax = plt.subplots()
ax.bar(list(quantity_by_class.keys()), [val / 1e6 for val in quantity_by_class.values()])
ax.set_xlabel('Klasa')
ax.set_xticks(list(classes_ASPRS.keys())) 
ax.set_ylabel('Liczba punktów [mln]')
ax.set_title('Liczba punktów w klasach')
plt.tight_layout() 
plt.show()

# visualize point cloud by class
visualize_point_cloud_by_class(xt, yt, zt, classification)