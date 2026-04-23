import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import shap
import matplotlib.pyplot as plt
import os

# Configuration
MICRO_FILE = "data/micro_features.csv"
MACRO_FILE = "data/macro_features.csv"
LST_FILE = "data/lst_data.csv" # Assumes LST data is extracted to CSV format
OUTPUT_DIR = "data/model_results"

def train_and_explain():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Load Data
    print("Loading data...")
    try:
        micro_df = pd.read_csv(MICRO_FILE)
        macro_df = pd.read_csv(MACRO_FILE)
        lst_df = pd.read_csv(LST_FILE) # Should contain 'filename' and 'LST' columns
    except FileNotFoundError as e:
        print(f"Data file not found: {e}")
        # Create dummy data for demonstration if files don't exist
        print("Creating dummy data for demonstration...")
        N = 100
        micro_df = pd.DataFrame({'filename': [f'img_{i}.jpg' for i in range(N)], 
                                 'vegetation': np.random.rand(N), 
                                 'building': np.random.rand(N)})
        macro_df = pd.DataFrame({'filename': [f'img_{i}.jpg' for i in range(N)], 
                                 'shadow_ratio': np.random.rand(N)})
        lst_df = pd.DataFrame({'filename': [f'img_{i}.jpg' for i in range(N)], 
                               'LST': 30 + 5 * np.random.rand(N)})

    # Merge Data
    df = micro_df.merge(macro_df, on='filename').merge(lst_df, on='filename')
    
    # Drop non-feature columns
    feature_cols = [c for c in df.columns if c not in ['filename', 'LST', 'id', 'lat', 'lon']]
    X = df[feature_cols]
    y = df['LST']
    
    print(f"Features: {feature_cols}")
    # Save merged data for spatial analysis
    merged_data_path = "data/merged_data.csv"
    df.to_csv(merged_data_path, index=False)
    print(f"Merged data saved to {merged_data_path}")
    
    # 2. Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Train Random Forest
    print("Training Random Forest model...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # 4. Evaluation
    y_pred = rf.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"MSE: {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    
    # 5. SHAP Analysis
    print("Running SHAP analysis...")
    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_test)
    
    # Summary Plot
    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False)
    plt.savefig(os.path.join(OUTPUT_DIR, "shap_summary.png"))
    plt.close()
    
    # Dependence Plot for Vegetation (if exists)
    if 'vegetation' in X.columns:
        plt.figure()
        shap.dependence_plot("vegetation", shap_values, X_test, show=False)
        plt.savefig(os.path.join(OUTPUT_DIR, "shap_dependence_vegetation.png"))
        plt.close()
        
    print(f"Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    train_and_explain()
