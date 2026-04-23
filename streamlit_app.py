import streamlit as st
import os

# Set page config
st.set_page_config(
    page_title="DeepStreetHeat | Interactive GIS Explorer",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit header/footer for a cleaner look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 配置区域 ---
# 如果您将街景图片上传到了 GitHub，请在此处填写 Raw 链接
# 格式示例: "https://raw.githubusercontent.com/您的用户名/仓库名/分支名/web_demo/data/svi_images/"
GITHUB_IMAGE_BASE_URL = "https://raw.githubusercontent.com/TongYao026/DeepStreetHeat/main/data/svi_images/" 

def load_web_demo():
    """Bundles index.html, styles.css, app.js and points_data.js into a single HTML string."""
    base_path = "web_demo"
    
    # Read HTML
    with open(os.path.join(base_path, "index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Read CSS
    with open(os.path.join(base_path, "styles.css"), "r", encoding="utf-8") as f:
        css_content = f.read()
    
    # Read Data
    with open(os.path.join(base_path, "data", "points_data.js"), "r", encoding="utf-8") as f:
        data_content = f.read()
        
    # Read JS Logic
    with open(os.path.join(base_path, "app.js"), "r", encoding="utf-8") as f:
        js_content = f.read()

    # 1. Inject CSS
    html_content = html_content.replace(
        '<link rel="stylesheet" href="./styles.css" />',
        f'<style>{css_content}</style>'
    )
    
    # 2. Inject Data and JS Logic
    # We replace the script tag that loads app.js with our bundled script
    bundled_script = f"""
    <script>
    window.IMAGE_BASE_URL = "{GITHUB_IMAGE_BASE_URL}";
    {data_content}
    {js_content}
    </script>
    """
    html_content = html_content.replace(
        '<script id="main-script" src="./app.js"></script>',
        bundled_script
    )
    
    return html_content

# Render the bundled HTML
html_string = load_web_demo()
st.components.v1.html(html_string, height=900, scrolling=True)
