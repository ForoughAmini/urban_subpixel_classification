# Import packages
import os
import numpy
from utils import *
from osgeo import gdal

def CorrectShadowFraction(Shadow, Stack, OutputFolder, NoDataValueShadow=0):
   
    # Read input data
    ShadowDataset = gdal.Open(Shadow)
    StackDataset = gdal.Open(Stack)

    ShadowArray = ShadowDataset.ReadAsArray()
    StackArray = StackDataset.ReadAsArray()

    # Get projection and geotransform
    prj = ShadowDataset.GetProjection()
    extent = ShadowDataset.GetGeoTransform()

    # Verify that Stack is a multiband raster
    if StackArray.ndim != 3:
        raise ValueError("Stack must be a multiband raster.")

    # Verify spatial dimensions
    if ShadowArray.shape != StackArray.shape[1:]:
        raise ValueError(
            "Shadow and Stack images have different dimensions."
        )

    # Check spatial alignment
    if ShadowDataset.GetProjection() != StackDataset.GetProjection():
        raise ValueError(
            "Shadow and Stack images have different projections."
        )

    # Close datasets
    ShadowDataset = None
    StackDataset = None

    # Correct NoData values in shadow
    ShadowArray[ShadowArray == NoDataValueShadow] = 0

    # Calculate sum of VIS fractions
    SumVIS = numpy.sum(StackArray, axis=0)

    # Create output folder if it doesn't exist
    os.makedirs(OutputFolder, exist_ok=True)

    # Get input filename
    StackName = os.path.splitext(os.path.basename(Stack))[0]

    # Loop through VIS bands
    for band in range(StackArray.shape[0]):

        # Calculate shadow correction
        ShadowContribution = numpy.divide(
            numpy.multiply(StackArray[band], ShadowArray),
            SumVIS,
            out=numpy.zeros_like(ShadowArray, dtype=float),
            where=SumVIS != 0
        )

        Stack_band_adapted = StackArray[band] + ShadowContribution

        # Define output path
        OutputNamePath = os.path.join(
            OutputFolder,
            f'{StackName}_band_{band+1}_shadow_corrected.tif'
        )

        # Save output raster
        save_geotiff(
            OutputNamePath,
            Stack_band_adapted,
            prj,
            extent
        )

    print('Shadow correction finalized.')

Shadow = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\qgis_outputs\APEX_MESMA_shadow.tif"
Stack = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\qgis_outputs\APEX_MESMA_VIS.tif"
OutputFolder=r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\test"

# Apply shadow correction
CorrectShadowFraction(Shadow, Stack, OutputFolder)