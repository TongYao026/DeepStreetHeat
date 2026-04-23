import pandas as pd
import numpy as np

def generate_stats():
    # Load data
    try:
        micro_df = pd.read_csv("data/micro_features.csv")
        macro_df = pd.read_csv("data/macro_features.csv")
        lst_df = pd.read_csv("data/lst_data.csv")
        
        # Merge data based on filename (assuming filenames are unique keys in features)
        # Note: LST data has 'filename' column
        merged = pd.merge(lst_df, micro_df, on="filename", how="inner")
        merged = pd.merge(merged, macro_df, on="filename", how="inner")
        
        # Calculate stats
        stats = {}
        
        # LST Stats
        stats['LST_mean'] = merged['LST'].mean()
        stats['LST_std'] = merged['LST'].std()
        stats['LST_min'] = merged['LST'].min()
        stats['LST_max'] = merged['LST'].max()
        
        # Feature Stats
        features = ['vegetation', 'sky', 'building', 'road', 'shadow_ratio', 'sky_brightness']
        for f in features:
            if f in merged.columns:
                stats[f'{f}_mean'] = merged[f].mean()
                stats[f'{f}_std'] = merged[f].std()
        
        # Correlation with LST
        correlations = merged[features + ['LST']].corr()['LST'].drop('LST')
        
        print("--- Descriptive Statistics ---")
        for k, v in stats.items():
            print(f"{k}: {v:.4f}")
            
        print("\n--- Correlations with LST ---")
        print(correlations)
        
        return stats, correlations

    except Exception as e:
        print(f"Error calculating stats: {e}")
        return None, None

if __name__ == "__main__":
    generate_stats()
