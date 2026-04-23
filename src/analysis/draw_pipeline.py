import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_pipeline():
    fig, ax = plt.subplots(figsize=(14, 3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    steps = [
        ("Data Acquisition\n(SVI + LST)", "Google Maps API\nEarth Engine"),
        ("Preprocessing\n(Cleaning)", "Cloud Masking\nAnnual Mean"),
        ("Feature Extraction\n(Computer Vision)", "HSV Seg.\nMacro/Stat Features"),
        ("Aggregation\n(Point Level)", "Mean of 4 directions\nData Merging"),
        ("Modeling\n(Machine Learning)", "Gradient Boosting\n5-Fold CV"),
        ("Spatial Diagnostics\n(Validation)", "Residual Map\nSpatial Block CV")
    ]
    
    n = len(steps)
    box_width = 0.12
    gap = (1.0 - n * box_width) / (n + 1)
    
    for i, (title, subtitle) in enumerate(steps):
        x = gap + i * (box_width + gap)
        y = 0.4
        
        # Box
        rect = patches.FancyBboxPatch((x, y), box_width, 0.4, boxstyle="round,pad=0.02", 
                                      linewidth=1.5, edgecolor='#333333', facecolor='#E6F3FF')
        ax.add_patch(rect)
        
        # Text
        ax.text(x + box_width/2, y + 0.25, title, 
                ha='center', va='center', fontsize=9, fontweight='bold', color='#003366')
        ax.text(x + box_width/2, y + 0.1, subtitle, 
                ha='center', va='center', fontsize=7.5, color='#444444')
        
        # Arrow
        if i < n - 1:
            arrow_x = x + box_width + 0.005
            arrow_y = y + 0.2
            ax.arrow(arrow_x, arrow_y, gap - 0.015, 0, 
                     head_width=0.02, head_length=0.01, fc='gray', ec='gray')
            
    plt.title("DeepStreetHeat Research Framework", fontsize=14, fontweight='bold', y=0.9)
    plt.tight_layout()
    plt.savefig('data/pipeline.png', dpi=300, bbox_inches='tight')
    print("Pipeline diagram saved to data/pipeline.png")

if __name__ == "__main__":
    draw_pipeline()
