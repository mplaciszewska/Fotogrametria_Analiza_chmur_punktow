import laspy
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.vstack((x, y, z)).T
    print("Liczba punktów:", len(points))
    return points

def compute_density(chmura_punktow, radius, density_mode):
    pcd_tree = o3d.geometry.KDTreeFlann(chmura_punktow)
    densities = []
    surface_area = np.pi * radius**2 

    for i in range(len(chmura_punktow.points)):
        query_point = chmura_punktow.points[i]  
        [k, idx, _] = pcd_tree.search_radius_vector_xd(query_point, radius)  
        if density_mode == '2D':
            density = (k-1)/ surface_area 
            densities.append(density)
        elif density_mode == '3D':
            density = (k-1)/ (4/3 * np.pi * radius**3)
            densities.append(density)

    return np.array(densities)

las_file = input("Podaj ścieżkę do pliku .laz: ")

try:
    las = laspy.read(las_file)
except Exception as e:
    print(f"Błąd przy wczytywaniu pliku: {e}")
    exit()

density_mode = input("Podaj tryb obliczania gęstości (2D/3D): ")
try: 
    assert density_mode in ['2D', '3D', '2d', '3d']
except AssertionError:
    print("Podano nieprawidłowy tryb obliczania gęstości")
    exit()

ground_only = input("Czy chcesz obliczyć gęstość tylko dla punktów klasy 'ground'? (t/n): ")
try:
    assert ground_only in ['t', 'n', 'T', 'N']
except AssertionError:
    print("Podano nieprawidłową odpowiedź")
    exit()

las = laspy.read(las_file)
points = read_las(las)

# allowed_classes = [0,1,2,3,4,5,6,9]
# where_not_noise = np.isin(las["classification"], allowed_classes)
# points = points[where_not_noise]

# choose only ground points
if ground_only == 't' or ground_only == 'T':
        ground_class_mask = las.classification == 2  # 2 oznacza klasę gruntu
        points = points[ground_class_mask]

translate_vector = las.header.min
points_translated = points - translate_vector
xt, yt, zt= points_translated[:, 0], points_translated[:, 1], points_translated[:, 2]
las_points = np.vstack((xt,yt,zt)).transpose()

chmura_punktow = o3d.geometry.PointCloud()
chmura_punktow.points = o3d.utility.Vector3dVector(las_points)

radius = 1 

def compute_density_quick(chmura_punktow, radius, density_mode):
    kdtree = cKDTree(chmura_punktow)
    neighbours_of_point = kdtree.query_ball_point(chmura_punktow[::10000], r=radius, workers = -1)
    densities = [len(neighbours) for neighbours in neighbours_of_point]

    if density_mode == "2D":
        densities = [(len(neighbours))/(np.pi * radius**2) for neighbours in neighbours_of_point]
    elif density_mode == "3D":
        densities = [(len(neighbours))/(4/3 * np.pi * radius**3) for neighbours in neighbours_of_point]

    return densities

densities = compute_density_quick(las_points, radius, density_mode)
    
# histogram
plt.figure(figsize=(10, 6))
plt.hist(densities, bins=30, color='steelblue', edgecolor='black', alpha=0.7)

plt.xlabel(f'Gęstość punktów na {"m²" if density_mode.lower() == "2d" else "m³"}')
plt.ylabel('Liczba punktów')
plt.title('Histogram rozkładu gęstości punktów')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

