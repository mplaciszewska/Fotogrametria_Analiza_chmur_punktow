import laspy
import open3d as o3d
import numpy as np

allowed_classes = [2,3,4,5,6]

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.vstack((x, y, z)).T
    print("Liczba punktów:", len(points))
    return points

las_file = r"76193_1196263_M-34-5-C-b-4-4-3-4.laz"
las = laspy.read(las_file)
points = read_las(las)

def visualize_point_cloud(xt, yt, zt, intensity):
    las_points = np.vstack((xt,yt,zt)).transpose()
    chmura_punktow = o3d.geometry.PointCloud()
    chmura_punktow.points = o3d.utility.Vector3dVector(las_points)

    colors = np.stack([intensity, intensity, intensity], axis=1)
    chmura_punktow.colors = o3d.utility.Vector3dVector(colors)

    o3d.visualization.draw_geometries_with_editing([chmura_punktow],window_name='Chmura punktów')

def visualize_point_cloud_kdtree(xt, yt, zt, intensity, radius, query_point_index):
    las_points = np.vstack((xt,yt,zt)).transpose()
    chmura_punktow = o3d.geometry.PointCloud()
    chmura_punktow.points = o3d.utility.Vector3dVector(las_points)

    colors = np.stack([intensity, intensity, intensity], axis=1)
    chmura_punktow.colors = o3d.utility.Vector3dVector(colors)

    pcd_tree = o3d.geometry.KDTreeFlann(chmura_punktow)
    query_point = chmura_punktow.points[query_point_index]

    [k, idx, _] = pcd_tree.search_radius_vector_3d(query_point, radius) # k - liczba znalezionych punktów, idx - indeksy znalezionych punktów, _ - tablica z dystansami do znalezionych punktów
    np.asarray(chmura_punktow.colors)[idx[1:], :] = [0, 1, 0] # [1:] -> wyrzucany jest pierwszy punkt (punkt zapytania)

    o3d.visualization.draw_geometries([chmura_punktow]) 

def point_extraction_based_on_the_class(las, class_type):
    if class_type == 'buildings':
        print('Ekstrakcja punktów budynków')
        buildings_only = np.where(las.classification == 6)
        buildings_points = np.vstack((las.x[buildings_only], las.y[buildings_only], las.z[buildings_only])).T
        return buildings_points
    elif class_type == 'vegetation':
        print('Ekstrakcja punktów roślinności')
        vegetation_low = np.where(las.classification == 3)
        vegetation_medium = np.where(las.classification == 4)
        vegetation_high = np.where(las.classification == 5)
        vegetation_points = np.vstack((
            np.vstack((las.x[vegetation_low], las.y[vegetation_low], las.z[vegetation_low])).T,
            np.vstack((las.x[vegetation_medium], las.y[vegetation_medium], las.z[vegetation_medium])).T,
            np.vstack((las.x[vegetation_high], las.y[vegetation_high], las.z[vegetation_high])).T
        ))
        return vegetation_points
    else:
        print('Ekstrakcja punktów gruntu')
        ground_only = np.where(las.classification == 2)
        ground_points = np.vstack((las.x[ground_only], las.y[ground_only], las.z[ground_only])).T
        return ground_points
    
def get_intensities_for_class(las, class_type):
    if class_type == 'buildings':
        class_indices = np.where(las.classification == 6)[0]
    elif class_type == 'vegetation':
        class_indices = np.where(np.isin(las.classification, [3, 4, 5]))[0] 
    elif class_type == 'ground':
        class_indices = np.where(las.classification == 2)[0]
    else:
        raise ValueError(f"Nieznana klasa: {class_type}")

    intensities_for_class = las.intensity[class_indices]

    intensities_normalized = np.clip(
        (intensities_for_class - np.quantile(intensities_for_class, 0.05)) /
        (np.quantile(intensities_for_class, 0.95) - np.quantile(intensities_for_class, 0.05)),
        0, 1
    )
    return intensities_normalized

def save_point_cloud_to_las(points, intensities, file_name):
    header = laspy.LasHeader(point_format=3, version="1.2")
    header.offsets = np.min(points, axis=0) 
    header.scales = np.array([0.1, 0.1, 0.1]) 

    with laspy.open(file_name, mode="w", header=header) as writer:
        point_record = laspy.ScaleAwarePointRecord.zeros(points.shape[0], header=header)
   
        point_record.x = points[:, 0]
        point_record.y = points[:, 1]
        point_record.z = points[:, 2]
 
        point_record.intensity = intensities
        writer.write_points(point_record)

# save_point_cloud_to_las(ground_points, intensity_ground, r"output\ground_points.las")
# save_point_cloud_to_las(buildings_points, intensity_buildings, r"output\buildings_points.las")
# save_point_cloud_to_las(vegetation_points, intensity_vegetation, r"output\vegetation_points.las")

# --------------------- ALL ALLOWED CLASSES ---------------------
intensity = las.intensity
intensity = np.clip(
        (intensity - np.quantile(intensity, 0.05)) /
        (np.quantile(intensity, 0.95) - np.quantile(intensity, 0.05)),
        0, 1
    )

# filtracja punktów po klasach
where_not_noise = np.isin(las["classification"], allowed_classes)
points = points[where_not_noise]
intensity = intensity[where_not_noise]

# translacja do układu środka
translate_vector = las.header.min
points_translated = points - translate_vector
xt, yt, zt= points_translated[:, 0], points_translated[:, 1], points_translated[:, 2]

# visualize_point_cloud(xt, yt, zt, intensity)
visualize_point_cloud_kdtree(xt, yt, zt, intensity, 20, 50)

# ------------------------- GROUND ----------------------------
ground_points = point_extraction_based_on_the_class(las, 'ground')
intensity_ground = get_intensities_for_class(las, 'ground')
xt_ground, yt_ground, zt_ground = ground_points[:, 0], ground_points[:, 1], ground_points[:, 2]
# visualize_point_cloud(xt_ground, yt_ground, zt_ground, intensity_ground)
visualize_point_cloud_kdtree(xt_ground, yt_ground, zt_ground, intensity_ground, 20, 50)

# ------------------------- BUILDINGS ----------------------------
buildings_points = point_extraction_based_on_the_class(las, 'buildings')
intensity_buildings = get_intensities_for_class(las, 'buildings')
xt_buildings, yt_buildings, zt_buildings = buildings_points[:, 0], buildings_points[:, 1], buildings_points[:, 2]
# visualize_point_cloud(xt_buildings, yt_buildings, zt_buildings, intensity_buildings)
visualize_point_cloud_kdtree(xt_buildings, yt_buildings, zt_buildings, intensity_buildings, 20, 50)

# ------------------------- VEGETATION ----------------------------
vegetation_points = point_extraction_based_on_the_class(las, 'vegetation')
intensity_vegetation= get_intensities_for_class(las, 'vegetation')
xt_vegetation, yt_vegetation, zt_vegetation = vegetation_points[:, 0], vegetation_points[:, 1], vegetation_points[:, 2]
# visualize_point_cloud(xt_vegetation, yt_vegetation, zt_vegetation, intensity_vegetation)
visualize_point_cloud_kdtree(xt_vegetation, yt_vegetation, zt_vegetation, intensity_vegetation, 20, 50)

