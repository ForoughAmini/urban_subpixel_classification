import numpy
from math import sqrt
from osgeo import gdal
from sklearn import metrics
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from scipy.interpolate import interpn


def save_geotiff(output_path, output_array, projection, geotransform,
                 nodata=-9999, data_type=gdal.GDT_Float64):

    rows, cols = output_array.shape

    output = gdal.GetDriverByName('GTiff').Create(
        output_path, cols, rows, 1, data_type
    )

    output.SetProjection(projection)
    output.SetGeoTransform(geotransform)

    band = output.GetRasterBand(1)
    band.WriteArray(output_array)
    band.SetNoDataValue(nodata)

    output = None

def save_text_file(output_path, content):
    with open(output_path, 'w') as f:
        f.write(content)

def scatter(x, y, pc_x, pc_y, output_path):
    # Create figure
    fig, ax = plt.subplots()

    # Calculate point density using a 2D histogram
    data, x_e, y_e = numpy.histogram2d(x, y, bins=50)

    # Calculate bin centres
    x_centres = 0.5 * (x_e[1:] + x_e[:-1])
    y_centres = 0.5 * (y_e[1:] + y_e[:-1])

    # Interpolate density values for individual points
    z = interpn(
        (x_centres, y_centres),
        data,
        numpy.vstack([x, y]).T,
        method="linear",
        bounds_error=False
    )

    # Sort points according to density
    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    # Create scatter plot
    ax.scatter(x, y, c=z, cmap=plt.cm.jet, s=0.1)

    # Set dynamic labels and title
    ax.set_xlabel(pc_x)
    ax.set_ylabel(pc_y)
    ax.set_title(f"{pc_x} vs {pc_y}")

    # Save plot
    fig.savefig(output_path, dpi=300, bbox_inches="tight")

    # Close figure
    plt.close(fig)

def SetValueNaN(Array):
    # Get NoData value from the first pixel
    NoDataValue = Array[0, 0]

    # Replace NoData values with NaN
    Array = Array.astype(float)
    Array[Array == NoDataValue] = numpy.nan

    return Array

def GetNoNaNValues(ArrayRef, ArrayPred):

    # Identify pixels that are valid in both arrays
    ValidMask = ~numpy.isnan(ArrayRef) & ~numpy.isnan(ArrayPred)

    # Extract corresponding valid values
    NoNaNValues_Ref = ArrayRef[ValidMask]
    NoNaNValues_Pred = ArrayPred[ValidMask]

    return NoNaNValues_Ref, NoNaNValues_Pred

def PlotFractionValidation(ArrayRef, ArrayPred, ClassName, OutputPath, MarkerSize=0.05):

    ArrayRef = numpy.asarray(ArrayRef).ravel()
    ArrayPred = numpy.asarray(ArrayPred).ravel()

    # Calculate error metrics
    MAE = round(metrics.mean_absolute_error(ArrayRef, ArrayPred), 2)
    RMSE = round(sqrt(metrics.mean_squared_error(ArrayRef, ArrayPred)), 2)

    # Create plot
    fig, ax = plt.subplots(figsize=(5, 5))

    ax.axis('equal')

    ax.scatter(ArrayRef, ArrayPred, c='#D9A441', s=MarkerSize)

    ax.set_xlabel('Reference fraction', fontsize=8)
    ax.set_ylabel('Estimated fraction', fontsize=8)

    ax.set_title(f'{ClassName} fraction validation', fontsize=10)

    ax.set_ylim(-0.05, 1.1)
    ax.set_xlim(-0.05, 1.1)

    ax.annotate(f'MAE = {MAE}', xy=(0, 0.95), fontsize=8)
    ax.annotate(f'RMSE = {RMSE}', xy=(0, 0.85), fontsize=8)

    # Add 1:1 reference line
    line = mlines.Line2D([0, 1], [0, 1], color='black', linewidth=1)
    ax.add_line(line)

    # Save plot
    fig.savefig(OutputPath, dpi=300, bbox_inches='tight')

    plt.close(fig)

    return MAE, RMSE