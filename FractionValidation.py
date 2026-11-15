# Import packages
from osgeo import gdal
import os
from utils import *

def ValidateFraction(Reference, Prediction, BandNumber, ClassName, OutputFolder, MarkerSize=0.05):

    # Read input rasters
    RefDataset = gdal.Open(Reference)
    PredDataset = gdal.Open(Prediction)

    Ref = RefDataset.ReadAsArray()
    Pred = PredDataset.ReadAsArray()

    # Get number of prediction bands
    NumberBands = PredDataset.RasterCount

    # Check selected band number
    if BandNumber < 1 or BandNumber > NumberBands:
        raise ValueError(
            f'BandNumber must be between 1 and {NumberBands}.'
        )

    # Select prediction band
    Pred = Pred[BandNumber - 1]

    # Check image dimensions
    if Ref.shape != Pred.shape:
        raise ValueError(
            f'Reference and prediction images have different dimensions: '
            f'{Ref.shape} and {Pred.shape}.'
        )

    # Close datasets
    RefDataset = None
    PredDataset = None

    # Correct arrays for NoData values
    Ref_NaN = SetValueNaN(Ref)
    Pred_NaN = SetValueNaN(Pred)

    # Extract valid corresponding pixels
    Ref_ValidValues, Pred_ValidValues = GetNoNaNValues(
        Ref_NaN, Pred_NaN
    )

    if len(Ref_ValidValues) == 0:
        raise ValueError('No valid corresponding pixels were found.')

    # Define output path
    os.makedirs(OutputFolder, exist_ok=True)

    OutputName = f'{ClassName}_fraction_validation.png'
    OutputPath = os.path.join(OutputFolder, OutputName)

    # Generate validation plot
    MAE, RMSE = PlotFractionValidation(
        Ref_ValidValues,
        Pred_ValidValues,
        ClassName,
        OutputPath,
        MarkerSize
    )

    print(f'Validation completed for {ClassName}.')
    print(f'MAE: {MAE}')
    print(f'RMSE: {RMSE}')
    print(f'Plot saved to: {OutputPath}')

    return MAE, RMSE

Reference = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\AEOT_exercise_1_unmixing\AEOT_exercise_1_unmixing\Data\Part2\ReferenceFractions_VIS_Impervious.tif" #write the full path of the file (e.g. C:/Users/zorro/file.tif)
Prediction = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\qgis_outputs\APEX_Unmixing_Equalized.tif"
OutputFolder = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\test"

# Validate class fraction
MAE, RMSE = ValidateFraction(
    Reference,
    Prediction,
    BandNumber=1,
    ClassName='Impervious',
    OutputFolder=OutputFolder
)