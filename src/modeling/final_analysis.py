
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.inspection import PartialDependenceDisplay

# Configuration
MERGED_DATA_PATH = "data/aggregated_features.csv"
SEGFORMER_DATA_PATH = "data/segformer_features.csv"
OUTPUT_DIR = "data/model_results"
PLOTS_DIR = "data/model_results"

# Load Data
print("Loading data...")
df_main = pd.read_csv(MERGED_DATA_PATH)
df_seg = pd.read_csv(SEGFORMER_DATA_PATH)

# Prepare ID for SegFormer data
# filename format: "123456_0.jpg" -> id: 123456
df_seg['id'] = df_seg['filename'].apply(lambda x: int(x.split('_')[0]))

# Merge
df = pd.merge(df_main, df_seg, on='id', how='inner', suffixes=('', '_seg'))
print(f"Merged dataset shape: {df.shape}")

# Feature Name Mapping (to match script variables)
column_mapping = {
    'vegetation': 'Vegetation',
    'sky': 'Sky',
    'building': 'Building',
    'road': 'Road',
    'shadow_ratio': 'Shadow',
    'entropy': 'h_entropy', # Check if it is entropy or h_entropy in file. It is 'entropy' in file.
    'colorfulness': 'Colorfulness',
    'LST': 'LST_Celsius'
}
# Only rename if they exist
rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
df = df.rename(columns=rename_dict)

# Update Feature Lists based on actual columns
# The dataframe columns have been renamed to Capitalized versions where applicable
features_hsv = ['Vegetation', 'Sky', 'Building', 'Road', 'Shadow', 'h_std', 'h_entropy', 'Colorfulness'] 
# Filter to ensure they exist
available_cols = df.columns.tolist()
features_hsv = [c for c in features_hsv if c in available_cols]
features_poi = ['poi_density']
features_seg = ['seg_vegetation', 'seg_sky', 'seg_building', 'seg_road']

target = 'LST_Celsius'

print(f"Features available for HSV: {features_hsv}")
print(f"Features available for SegFormer: {features_seg}")

# Prepare X and y
# Drop NaNs
df = df.dropna(subset=[target] + features_hsv + features_poi + features_seg)
y = df[target]
print(f"Final samples for training: {len(df)}")

# Models to Compare
models_config = {
    "Baseline (Mean)": {
        "features": [],
        "model": DummyRegressor(strategy="mean")
    },
    "Traditional (HSV+POI)": {
        "features": features_hsv + features_poi,
        "model": GradientBoostingRegressor(random_state=42, n_estimators=100, max_depth=3)
    },
    "Deep Learning (SegFormer+POI)": {
        "features": features_seg + features_poi,
        "model": GradientBoostingRegressor(random_state=42, n_estimators=100, max_depth=3)
    },
    "Combined (All Features)": {
        "features": features_hsv + features_poi + features_seg,
        "model": GradientBoostingRegressor(random_state=42, n_estimators=100, max_depth=3)
    }
}

results = []

print("Training and evaluating models...")
kf = KFold(n_splits=5, shuffle=True, random_state=42)

for name, config in models_config.items():
    if name == "Baseline (Mean)":
        X = df[features_hsv] # Dummy doesn't care about features
    else:
        X = df[config["features"]]
    
    model = config["model"]
    
    # Cross-validation
    r2_scores = cross_val_score(model, X, y, cv=kf, scoring='r2')
    rmse_scores = -cross_val_score(model, X, y, cv=kf, scoring='neg_root_mean_squared_error')
    
    # Fit on full data for feature importance
    model.fit(X, y)
    
    results.append({
        "Model": name,
        "R2": r2_scores.mean(),
        "RMSE": rmse_scores.mean(),
        "Model_Obj": model,
        "Features": config["features"]
    })
    
    print(f"{name}: R2={r2_scores.mean():.4f}, RMSE={rmse_scores.mean():.4f}")

# Results DataFrame
res_df = pd.DataFrame(results)
print("\nFinal Comparison:")
print(res_df[['Model', 'R2', 'RMSE']])

# 1. Plot Model Comparison
plt.figure(figsize=(10, 6))
sns.barplot(data=res_df, x='Model', y='R2', palette='viridis')
plt.title('Model R² Comparison: Traditional vs Deep Learning')
plt.ylabel('R² Score')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/model_comparison_r2.png")
plt.close()

# 2. Feature Importance (Best Model - likely Combined or DL)
best_model_row = res_df.loc[res_df['R2'].idxmax()]
best_model = best_model_row['Model_Obj']
best_features = best_model_row['Features']

if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feat_imp = pd.DataFrame({'Feature': best_features, 'Importance': importances})
    feat_imp = feat_imp.sort_values(by='Importance', ascending=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(data=feat_imp, x='Importance', y='Feature', palette='magma')
    plt.title(f'Feature Importance ({best_model_row["Model"]})')
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/best_model_importance.png")
    plt.close()
    
    # PDP for top 3 features
    top_3 = feat_imp['Feature'].head(3).tolist()
    X_best = df[best_features]
    
    fig, ax = plt.subplots(figsize=(12, 4))
    PartialDependenceDisplay.from_estimator(best_model, X_best, top_3, ax=ax)
    plt.suptitle(f"Partial Dependence Plots for Top 3 Features ({best_model_row['Model']})")
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/best_model_pdp.png")
    plt.close()

# 3. Correlation: SegFormer vs HSV
# Check correlation between 'seg_vegetation' and 'Vegetation' (HSV)
corr_cols = features_hsv + features_seg
corr_matrix = df[corr_cols].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0)
plt.title('Correlation Matrix: HSV vs SegFormer Features')
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/feature_correlation_hsv_seg.png")
plt.close()

# Scatter plot for Vegetation comparison
plt.figure(figsize=(8, 8))
sns.scatterplot(data=df, x='Vegetation', y='seg_vegetation', alpha=0.5)
plt.plot([0, 1], [0, 1], 'r--')
plt.title('Vegetation Detection: HSV vs SegFormer')
plt.xlabel('HSV Vegetation Ratio')
plt.ylabel('SegFormer Vegetation Ratio')
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/vegetation_comparison.png")
plt.close()

print("Analysis complete. Plots saved.")
