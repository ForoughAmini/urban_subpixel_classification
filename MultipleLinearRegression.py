# Import packages
import os
import numpy
from utils import *
from osgeo import gdal
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def MultipleLinearRegression(Reference, Bands, FractionName,
        TestSize, OutputFolder, RandomState=42, MarkerSize=0.05):

    # Create output folder if it doesn't exist
    os.makedirs(OutputFolder, exist_ok=True)

    # Read reference data
    RefDataset = gdal.Open(Reference)
    Y = RefDataset.ReadAsArray()

    # Store original raster dimensions
    Rows, Cols = Y.shape

    # Get reference raster information
    RefProjection = RefDataset.GetProjection()
    RefGeoTransform = RefDataset.GetGeoTransform()

    # Flatten reference data
    Y = Y.flatten()

    # Read spectral bands
    BandsDataset = gdal.Open(Bands)
    SpectralBands = BandsDataset.ReadAsArray()

    # Check spatial dimensions
    if SpectralBands.shape[1:] != (Rows, Cols):
        raise ValueError(
            "Reference and spectral images have different dimensions."
        )

    # Check spatial alignment
    if RefProjection != BandsDataset.GetProjection():
        raise ValueError(
            "Reference and spectral images have different projections."
        )

    # Get output raster information from spectral dataset
    prj = BandsDataset.GetProjection()
    extent = BandsDataset.GetGeoTransform()

    # Close datasets
    RefDataset = None
    BandsDataset = None

    # Prepare X
    X = []

    for i in range(SpectralBands.shape[0]):

        band_i = SpectralBands[i].flatten()
        X.append(band_i)

    # Transpose X to obtain (pixels, bands)
    X = numpy.transpose(X)

    # Split X and Y
    X_train, X_validation, Y_train, Y_validation = train_test_split(X, Y,
        test_size=TestSize, random_state=RandomState)

    # Fit multiple linear regression
    reg = LinearRegression().fit(X_train, Y_train)

    # Write regression information
    reg_info = (
        "Multiple linear regression statistics:\n\n"
        f"Fraction: {FractionName}\n"
        f"Training samples: {len(Y_train)}\n"
        f"Validation samples: {len(Y_validation)}\n"
        f"Intercept = {numpy.around(reg.intercept_, decimals=3)}\n"
        f"Coefficients = {numpy.around(reg.coef_, decimals=3)}\n"
        f"R² (training) = "
        f"{numpy.around(reg.score(X_train, Y_train), decimals=2)}\n"
    )

    InformationPath = os.path.join(
        OutputFolder,
        f'MLR_{FractionName}_regression_information.txt'
    )

    save_text_file(InformationPath, reg_info)

    # Predict fraction for validation set
    Y_prediction = reg.predict(X_validation)

    ValidationPath = os.path.join(
        OutputFolder,
        f'MLR_{FractionName}_regression_validation.png'
    )

    MAE, RMSE = PlotFractionValidation(
        Y_validation,
        Y_prediction,
        FractionName,
        ValidationPath,
        MarkerSize
    )

    # Predict fractions for the entire image
    pred_image = reg.predict(X)

    # Reshape predictions to original raster dimensions
    pred_image_2D = pred_image.reshape(Rows, Cols)

    PredictionPath = os.path.join(
        OutputFolder,
        f'MLR_{FractionName}_regression_prediction.tif'
    )

    save_geotiff(
        PredictionPath,
        pred_image_2D,
        prj,
        extent
    )

    print(f'Regression completed for {FractionName}.')
    print(f'Validation MAE: {MAE}')
    print(f'Validation RMSE: {RMSE}')
    print(f'Prediction saved to: {PredictionPath}')

    return reg, MAE, RMSE


# Define input and parameters --> replace PATH with the actual path to the file
Reference=r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\AEOT_exercise_1_unmixing\AEOT_exercise_1_unmixing\Data\Part1\ReferenceImperviousFractions.tif"
Bands = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\Landsat8.tif"
OutputFolder = r"D:\GIS\Advanced Earth Observation\practical\Practicals_export\Exercise_1\Advance\image\test"


# Impervious fraction
reg_imp, MAE_imp, RMSE_imp = MultipleLinearRegression(
    Reference=Reference,
    Bands=Bands,
    FractionName='Impervious',
    TestSize=0.2,
    OutputFolder=OutputFolder
)