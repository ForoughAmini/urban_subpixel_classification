This project was developed as part of the [Advanced Earth Observation Techniques] (https://caliweb.vub.be/?page=course-offer&id=012698&anchor=1&target=pr&year=2627&language=en&output=html) course at Vrije Universiteit Brussel (VUB). The Python code builds on the concepts and coding techniques introduced during the course, which were further adapted, extended, and modified to meet the specific objectives of the project.

The project explores image analysis and sub-pixel land-cover classification using satellite and airborne remote sensing data.

## Data and Methods

### Part 1 – Leuven

Landsat 8 imagery was used to investigate the land-cover composition of Leuven, Belgium. The main methods included:

- Principal Component Analysis (PCA)
- Regression-Based Spectral Unmixing
- Multiple Linear Regression (MLR)

### Part 2 – Brussels

An APEX hyperspectral image covering Brussels, Belgium, was used to estimate impervious, soil, and vegetation (VIS) fractions. The methods included:

- Multiple Endmember Spectral Mixture Analysis (MESMA)
- Shadow correction
- Random Forest-based Regression Unmixing, using synthetic spectral mixtures

The resulting fraction maps were assessed using reference data and accuracy metrics, including Mean Absolute Error (MAE) and Root Mean Square Error (RMSE).
