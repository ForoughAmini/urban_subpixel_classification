# Import packages
import os
import numpy
from utils import *
from osgeo import gdal
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from itertools import combinations

def PCA_Analysis(InputImagery, NumberComponents, OutputFolder):

    # Create output folder if it doesn't exist
    os.makedirs(OutputFolder, exist_ok=True)

    # Read imagery and get imagery information
    dataset = gdal.Open(InputImagery)
    Image = dataset.ReadAsArray()
    prj = dataset.GetProjectionRef()
    extent = dataset.GetGeoTransform()
    dataset = None

    # Verify that the input imagery is multiband
    if Image.ndim != 3:
        raise ValueError("Input imagery must be a multiband raster.")

    # Verify the requested number of components
    if NumberComponents < 1 or NumberComponents > Image.shape[0]:
        raise ValueError(
            "NumberComponents must be between 1 and the number of input bands."
        )

    # Adapt shape from (bands, rows, cols) to (rows, cols, bands)
    Image_AdaptedAxisOrder = numpy.moveaxis(Image, 0, -1)

    # Adapt shape from 3D to 2D; new shape = (rows * cols, bands)
    Image_2D = Image_AdaptedAxisOrder.reshape(
        (Image_AdaptedAxisOrder.shape[0] * Image_AdaptedAxisOrder.shape[1],
         Image_AdaptedAxisOrder.shape[2])
    )

    # Fit PCA
    pca = PCA(n_components=NumberComponents)
    pca_output = pca.fit_transform(Image_2D)

    # Calculate PCA information
    pca_info = (
        f"Explained variance by the first {NumberComponents} principal components:\n"
        f"{pca.explained_variance_ratio_}\n\n"
        f"Total explained variance by the first {NumberComponents} principal components:\n"
        f"{round(numpy.sum(pca.explained_variance_ratio_), 2)}\n\n"
        f"Component matrix:\n"
        f"{pca.components_}"
    )

    # Save PCA information
    InformationPath = os.path.join(OutputFolder, 'PCA_information.txt')
    save_text_file(InformationPath, pca_info)

    # Reshape PCA output
    pca_output_reshape = pca_output.reshape(
        (Image_AdaptedAxisOrder.shape[0],
         Image_AdaptedAxisOrder.shape[1],
         NumberComponents)
    )

    # Write PCA outputs
    for i in range(NumberComponents):

        OutputArray = pca_output_reshape[:, :, i]
        OutputNamePath = os.path.join(
            OutputFolder, f'PCA_PC_{i+1}.tif'
        )

        save_geotiff(OutputNamePath, OutputArray, prj, extent)

    # Generate all possible pairs of PCA components
    PC_files = [
        os.path.join(OutputFolder, f'PCA_PC_{i}.tif')
        for i in range(1, NumberComponents + 1)
    ]

    # Generate scatter plots for all component pairs
    for file1, file2 in combinations(PC_files, 2):

        # Define input files
        PC_X = gdal.Open(file1).ReadAsArray().ravel()
        PC_Y = gdal.Open(file2).ReadAsArray().ravel()

        # Define output path
        pc_x = os.path.basename(file1).replace('.tif', '').replace('PCA_', '')
        pc_y = os.path.basename(file2).replace('.tif', '').replace('PCA_', '')

        OutputPath = os.path.join(
            OutputFolder, f'{pc_x}_{pc_y}_scatter.png'
        )

        # Create scatter plot
        scatter(PC_X, PC_Y, pc_x, pc_y, OutputPath)

    print('PCA processing finalized.')

# Define input and parameters 
InputImagery = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\normalized_Landsat8.tif"
OutputFolder = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\test"
NumberComponents = 3

# Run PCA
PCA_Analysis(InputImagery, NumberComponents, OutputFolder)