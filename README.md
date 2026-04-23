# DeepStreetHeat: Predicting Urban Land Surface Temperature from Street View Imagery

## Introduction
The Urban Heat Island (UHI) effect poses a significant environmental and public health challenge in high-density cities like Hong Kong. This project, **DeepStreetHeat**, integrates Street View Imagery (SVI), Geographic Information Systems (GIS), and deep learning to evaluate urban microclimates efficiently.

## Objective
1.  **Extract Visual Features**: Use deep learning (SegFormer) and image processing to extract 29 micro/macro visual features from SVI.
2.  **Model Relationship**: Train a Random Forest (RF) regression model to map these features to satellite-derived Land Surface Temperature (LST).
3.  **Explain & Map**: Use SHAP for interpretability and generate spatial distribution maps of thermal risks.

## Study Area
Yau Tsim Mong District, Hong Kong.

## Methodology
*   **Data Sources**:
    *   SVI: Google Street View API (~700 images).
    *   LST: Landsat-8 TIRS via Google Earth Engine (GEE).
    *   Street Network: OpenStreetMap (OSM).
*   **Analysis**:
    *   **Microscopic Features**: 19 indicators via SegFormer-B5 (semantic segmentation).
    *   **Macroscopic Features**: 10 indicators (e.g., shadow ratio) via OpenCV.
    *   **Modeling**: Random Forest Regression + SHAP.
    *   **Spatial Analysis**: IDW Interpolation & Hotspot Analysis.

## Project Structure
*   `data/`: Stores raw and processed data.
*   `src/`: Source code.
    *   `data_collection/`: Scripts for downloading SVI, LST, and OSM data.
    *   `feature_extraction/`: Scripts for image segmentation and processing.
    *   `modeling/`: Scripts for training models and SHAP analysis.
    *   `analysis/`: Scripts for spatial analysis and visualization.
*   `notebooks/`: Jupyter notebooks for exploration and visualization.

## Setup
1.  Install dependencies: `pip install -r requirements.txt`
2.  Configure API keys (Google Maps, Earth Engine).
