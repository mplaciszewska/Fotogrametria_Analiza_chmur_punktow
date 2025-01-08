import arcpy 


# create las dataset 
las_dataset = arcpy.CreateLasDataset_management(
    r"79529_1503958_M-34-5-C-b-4-4-3-4.las",
    r"output/las_dataset.lasd"
)

# las dataset to raster
arcpy.LasDatasetToRaster_conversion(
    las_dataset,
    r"C:\Users\mplaciszewska\Desktop\studia\geoinf_sem_5\ftp\projekt2\output\las_raster.tif",
    value_field = "ELEVATION",
    sampling_type="CELLSIZE",
    sampling_value = 2.0
)

