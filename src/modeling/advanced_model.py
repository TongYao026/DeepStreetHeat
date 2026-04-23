import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, KFold, GroupKFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.dummy import DummyRegressor
from sklearn.inspection import PartialDependenceDisplay
from sklearn.cluster import KMeans
import os

def advanced_analysis():
    print("Loading data...")
    try:
        # Load the aggregated file directly if it exists and has POI data
        if os.path.exists("data/aggregated_features.csv"):
            aggregated = pd.read_csv("data/aggregated_features.csv")
            print("Loaded existing aggregated features.")
        else:
            # Fallback to merging (shouldn't happen in this flow)
            print("Aggregated file not found, merging raw files...")
            micro_df = pd.read_csv("data/micro_features.csv")
            macro_df = pd.read_csv("data/macro_features.csv")
            stat_df = pd.read_csv("data/statistical_features.csv")
            lst_df = pd.read_csv("data/lst_data.csv")
            
            merged = pd.merge(lst_df, micro_df, on="filename", how="inner")
            merged = pd.merge(merged, macro_df, on="filename", how="inner")
            merged = pd.merge(merged, stat_df, on="filename", how="inner")
            
            if 'id' not in merged.columns:
                merged['id'] = merged['filename'].apply(lambda x: x.split('_')[0])
            
            feature_cols_raw = [
                'vegetation', 'sky', 'building', 'road', 
                'shadow_ratio', 'sky_brightness',
                'h_mean', 'h_std', 's_mean', 's_std', 'v_mean', 'v_std', 'entropy', 'colorfulness'
            ]
            agg_rules = {col: 'mean' for col in feature_cols_raw}
            agg_rules['LST'] = 'first'
            agg_rules['lat'] = 'first'
            agg_rules['lon'] = 'first'
            aggregated = merged.groupby('id').agg(agg_rules).reset_index()

        # Define Features
        feature_cols = [
            'vegetation', 'sky', 'building', 'road', 
            'shadow_ratio', 'sky_brightness',
            'h_mean', 'h_std', 's_mean', 's_std', 'v_mean', 'v_std', 'entropy', 'colorfulness'
        ]
        
        # Add POI Density if available
        if 'poi_density' in aggregated.columns:
            print("POI Data Detected! Including 'poi_density' in model.")
            feature_cols.append('poi_density')
            # Handle potential NaNs in POI
            aggregated['poi_density'] = aggregated['poi_density'].fillna(0)
        
        # Spatial Blocking
        if 'block_id' not in aggregated.columns:
            print("Creating Spatial Blocks...")
            coords = aggregated[['lat', 'lon']]
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            aggregated['block_id'] = kmeans.fit_predict(coords)
        
        X = aggregated[feature_cols]
        y = aggregated['LST']
        groups = aggregated['block_id']
        ids = aggregated['id']
        
        if not os.path.exists('data/model_results'):
            os.makedirs('data/model_results')

        # 1. Random CV
        print("Running Random 5-Fold CV...")
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        random_cv_scores = {'rmse': [], 'mae': [], 'r2': []}
        feature_importances_list = []
        
        y_true_all = []
        y_pred_all = []
        residuals_all = []
        ids_all = []
        
        for train_index, test_index in kf.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            ids_test = ids.iloc[test_index]
            
            gbr = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)
            gbr.fit(X_train, y_train)
            y_pred = gbr.predict(X_test)
            
            random_cv_scores['rmse'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
            random_cv_scores['mae'].append(mean_absolute_error(y_test, y_pred))
            random_cv_scores['r2'].append(r2_score(y_test, y_pred))
            
            feature_importances_list.append(gbr.feature_importances_)
            y_true_all.extend(y_test)
            y_pred_all.extend(y_pred)
            residuals_all.extend(y_test - y_pred)
            ids_all.extend(ids_test)

        # 2. Spatial Block CV
        print("Running Spatial Block CV...")
        gkf = GroupKFold(n_splits=5)
        spatial_cv_scores = {'rmse': [], 'mae': [], 'r2': []}
        
        for train_index, test_index in gkf.split(X, y, groups=groups):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            gbr_spatial = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)
            gbr_spatial.fit(X_train, y_train)
            y_pred_spatial = gbr_spatial.predict(X_test)
            
            spatial_cv_scores['rmse'].append(np.sqrt(mean_squared_error(y_test, y_pred_spatial)))
            spatial_cv_scores['mae'].append(mean_absolute_error(y_test, y_pred_spatial))
            spatial_cv_scores['r2'].append(r2_score(y_test, y_pred_spatial))

        # Metrics Summary
        rand_rmse = np.mean(random_cv_scores['rmse'])
        rand_mae = np.mean(random_cv_scores['mae'])
        rand_r2 = np.mean(random_cv_scores['r2'])
        
        spatial_rmse = np.mean(spatial_cv_scores['rmse'])
        spatial_mae = np.mean(spatial_cv_scores['mae'])
        spatial_r2 = np.mean(spatial_cv_scores['r2'])
        
        dummy = DummyRegressor(strategy="mean")
        dummy.fit(X, y)
        y_dummy_pred = dummy.predict(X)
        baseline_rmse = np.sqrt(mean_squared_error(y, y_dummy_pred))
        
        print(f"Random CV R2: {rand_r2:.4f}")
        print(f"Spatial CV R2: {spatial_r2:.4f}")

        # Save Metrics
        with open('data/model_results/metrics.txt', 'w') as f:
            f.write(f"Random CV (5-Fold):\n")
            f.write(f"RMSE: {rand_rmse:.4f}\n")
            f.write(f"MAE: {rand_mae:.4f}\n")
            f.write(f"R2: {rand_r2:.4f}\n\n")
            f.write(f"Spatial Block CV (5 Blocks):\n")
            f.write(f"RMSE: {spatial_rmse:.4f}\n")
            f.write(f"MAE: {spatial_mae:.4f}\n")
            f.write(f"R2: {spatial_r2:.4f}\n\n")
            f.write(f"Baseline RMSE: {baseline_rmse:.4f}\n")

        # Save Feature Importance
        importances_matrix = np.array(feature_importances_list)
        mean_importance = np.mean(importances_matrix, axis=0)
        std_importance = np.std(importances_matrix, axis=0)
        sorted_idx = np.argsort(mean_importance)
        pos = np.arange(sorted_idx.shape[0]) + .5
        
        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(feature_cols)))
        plt.barh(pos, mean_importance[sorted_idx], xerr=std_importance[sorted_idx], align='center', color=colors, capsize=5)
        plt.yticks(pos, np.array(feature_cols)[sorted_idx])
        plt.xlabel('Impurity-based Importance')
        plt.title('Feature Importance (Random CV)')
        plt.tight_layout()
        plt.savefig('data/model_results/gbr_importance.png', dpi=300)
        plt.close()

        # PDP Plots
        print("Generating PDPs...")
        final_model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)
        final_model.fit(X, y)
        
        # Add 'poi_density' to PDP list if present
        features_to_plot = ['sky', 'shadow_ratio', 'h_std']
        if 'poi_density' in X.columns:
            features_to_plot.append('poi_density')
            
        valid_features = [f for f in features_to_plot if f in X.columns]
        
        if valid_features:
            # Separate Plots
            for feat in valid_features:
                fig, ax = plt.subplots(figsize=(6, 4))
                PartialDependenceDisplay.from_estimator(final_model, X, [feat], ax=ax, kind='average')
                plt.title(f'PDP: {feat}')
                plt.tight_layout()
                plt.savefig(f'data/model_results/pdp_{feat}.png', dpi=300)
                plt.close()

        return rand_r2

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    advanced_analysis()
