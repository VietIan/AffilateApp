"""
Custom CSS Styles cho Streamlit App
"""


def get_custom_css() -> str:
    """Trả về custom CSS cho app"""
    return """
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Headers */
    h1 {
        color: #FF6B6B;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #4ECDC4;
    }
    
    /* Cards */
    .stExpander {
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        border: none;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 10px;
    }
    
    /* File uploader */
    .stFileUploader > div {
        border: 2px dashed #4ECDC4;
        border-radius: 15px;
        background-color: #f8f9fa;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Toast notifications */
    .stToast {
        background-color: #4ECDC4;
    }
    
    /* Image container */
    .stImage {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border-color: #e9ecef;
    }
    
    /* Text area */
    .stTextArea > div > div {
        border-radius: 10px;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e3f2fd;
        border-radius: 10px;
    }
    
    .stSuccess {
        background-color: #e8f5e9;
        border-radius: 10px;
    }
    
    .stWarning {
        background-color: #fff3e0;
        border-radius: 10px;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    
    /* Copy button styling */
    .copy-btn {
        background-color: #4ECDC4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        cursor: pointer;
    }
    
    /* Result cards */
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    /* Emoji styling */
    .emoji-large {
        font-size: 2rem;
    }
</style>
"""


def get_loading_animation() -> str:
    """HTML cho loading animation"""
    return """
<div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
    <div style="
        width: 50px;
        height: 50px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #FF6B6B;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    "></div>
</div>
<style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
"""
