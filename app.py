"""
🎬 Jewelry Viral Gen - TikTok Content Generator
Biến ảnh sản phẩm thành trọn bộ nguyên liệu làm video TikTok viral

Features:
- Upload ảnh sản phẩm trang sức
- AI phân tích và generate Visual Prompt cho Veo3
- Tự động đề xuất Title, Hook, Hashtags viral
- Gợi ý nhạc trending phù hợp với sản phẩm
- Lưu lịch sử vào Firebase
"""

import streamlit as st
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from core.content_generator import ContentGenerator
from core.prompt_engine import PromptEngine
from services.image_processor import ImageProcessor
from ui.components import (
    render_upload_section, 
    render_result_display,
    render_history_sidebar,
    render_music_status
)
from ui.styles import get_custom_css, get_loading_animation

# Thử import Firebase (có thể fail nếu chưa cài)
try:
    from firebase.db_service import FirebaseDB
    FIREBASE_AVAILABLE = True
except Exception as e:
    print(f"Firebase not available: {e}")
    FIREBASE_AVAILABLE = False

# Thử import Scraper
try:
    from scraper.tiktok_music import scrape_trending_music_sync
    SCRAPER_AVAILABLE = True
except Exception as e:
    print(f"Scraper not available: {e}")
    SCRAPER_AVAILABLE = False

# Thử import Video Generator
try:
    from core.video_generator import VideoGenerator
    VIDEO_AVAILABLE = True
except Exception as e:
    print(f"Video Generator not available: {e}")
    VIDEO_AVAILABLE = False


# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Jewelry Viral Gen",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ===== SESSION STATE =====
if "result" not in st.session_state:
    st.session_state["result"] = None
if "results" not in st.session_state:
    st.session_state["results"] = []
if "music_list" not in st.session_state:
    st.session_state["music_list"] = None
if "history" not in st.session_state:
    st.session_state["history"] = []
if "video_path" not in st.session_state:
    st.session_state["video_path"] = None
if "video_generating" not in st.session_state:
    st.session_state["video_generating"] = False


# ===== FUNCTIONS =====
@st.cache_resource
def get_generator():
    """Cache ContentGenerator để không khởi tạo lại mỗi lần"""
    return ContentGenerator()


@st.cache_resource
def get_firebase():
    """Cache Firebase connection"""
    if FIREBASE_AVAILABLE:
        try:
            return FirebaseDB()
        except:
            return None
    return None


@st.cache_resource
def get_video_generator():
    """Cache Video Generator"""
    if VIDEO_AVAILABLE:
        try:
            return VideoGenerator()
        except:
            return None
    return None


def load_music_list():
    """Load danh sách nhạc từ cache hoặc Firebase"""
    # Thử load từ Firebase trước
    db = get_firebase()
    if db:
        try:
            music_data = db.get_music_trending()
            if music_data and music_data.get("songs"):
                return music_data.get("songs", [])
        except:
            pass
    
    # Fallback: Load từ file cache local
    cache_path = os.path.join(os.path.dirname(__file__), "data", "music_cache.json")
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def scrape_and_update_music():
    """Scrape nhạc mới và cập nhật vào Firebase + cache"""
    if not SCRAPER_AVAILABLE:
        st.error("❌ Playwright chưa được cài đặt. Chạy: playwright install")
        return False
    
    with st.spinner("🎵 Đang scrape nhạc trending từ TikTok..."):
        try:
            songs = scrape_trending_music_sync(limit=15)
            
            if songs:
                # Lưu vào Firebase
                db = get_firebase()
                if db:
                    db.update_music_trending(songs)
                
                # Lưu vào cache local
                cache_path = os.path.join(os.path.dirname(__file__), "data", "music_cache.json")
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(songs, f, indent=2, ensure_ascii=False)
                
                st.session_state["music_list"] = songs
                st.success(f"✅ Đã cập nhật {len(songs)} bài hát trending!")
                return True
            else:
                st.warning("⚠️ Không scrape được nhạc. Sử dụng cache.")
                return False
                
        except Exception as e:
            st.error(f"❌ Lỗi scrape: {e}")
            return False


# ===== SIDEBAR =====
with st.sidebar:
    st.title("💎 Jewelry Viral Gen")
    st.caption("v1.0.0 | TikTok Affiliate Tool")
    
    st.divider()
    
    # Status indicators
    st.subheader("📊 Trạng Thái")
    
    # Gemini status
    generator = get_generator()
    if generator.test_connection():
        st.success("✅ Gemini AI: Connected")
    else:
        st.error("❌ Gemini AI: Disconnected")
    
    # Firebase status
    if FIREBASE_AVAILABLE and get_firebase():
        st.success("✅ Firebase: Connected")
    else:
        st.warning("⚠️ Firebase: Not configured")
    
    # Veo 3.0 status
    if VIDEO_AVAILABLE:
        st.success("✅ Veo 3.0: Ready")
    else:
        st.warning("⚠️ Veo 3.0: Not configured")
    
    st.divider()
    
    # Music section
    st.subheader("🎵 Nhạc Trending")
    
    music_list = st.session_state.get("music_list") or load_music_list()
    st.session_state["music_list"] = music_list
    
    if music_list:
        st.info(f"📀 {len(music_list)} bài hát trong database")
        with st.expander("Xem danh sách"):
            for song in music_list[:10]:
                st.write(f"🎵 {song.get('name', 'Unknown')} - {song.get('artist', '')}")
    else:
        st.warning("Chưa có dữ liệu nhạc")
    
    if st.button("🔄 Cập Nhật Nhạc Trending", use_container_width=True):
        scrape_and_update_music()
    
    st.divider()
    
    # History
    render_history_sidebar(st.session_state.get("history", []))


# ===== MAIN CONTENT =====
st.title("🎬 Jewelry Viral Gen")
st.markdown("**Biến ảnh sản phẩm → Trọn bộ nguyên liệu video TikTok trong 30 giây**")
st.caption("💡 Upload nhiều ảnh = các góc khác nhau của CÙNG 1 sản phẩm → AI sẽ phân tích tất cả")

st.divider()

# 2-column layout
col_left, col_right = st.columns([1, 1.2])

# ===== LEFT COLUMN: INPUT =====
with col_left:
    uploaded_files, product_type, style, notes, custom_prompt = render_upload_section()
    
    st.divider()
    
    # Generate button
    generate_disabled = not uploaded_files or len(uploaded_files) == 0
    
    num_files = len(uploaded_files) if uploaded_files else 0
    btn_text = f"🚀 Generate Content ({num_files} ảnh = 1 sản phẩm)" if num_files > 1 else "🚀 Generate Content"
    
    if st.button(
        btn_text, 
        type="primary", 
        use_container_width=True,
        disabled=generate_disabled
    ):
        if uploaded_files:
            with st.spinner("🧠 AI đang phân tích sản phẩm từ tất cả các ảnh..."):
                # Lấy ảnh đầu tiên làm ảnh chính
                main_image = uploaded_files[0].getvalue()
                processed_main, status = ImageProcessor.process_for_gemini(main_image)
                
                # Xử lý các ảnh phụ (nếu có)
                additional_images = []
                if len(uploaded_files) > 1:
                    for f in uploaded_files[1:]:
                        img_bytes = f.getvalue()
                        processed, _ = ImageProcessor.process_for_gemini(img_bytes)
                        if processed:
                            additional_images.append(processed)
                
                if processed_main:
                    st.info(f"📷 Đang phân tích {len(uploaded_files)} ảnh của sản phẩm...")
                    
                    # Get music list
                    music_list = st.session_state.get("music_list") or load_music_list()
                    
                    # Generate content với TẤT CẢ ảnh
                    generator = get_generator()
                    result = generator.generate(
                        image_data=processed_main,
                        product_type=product_type,
                        price="",  # Không cần giá cho affiliate
                        notes=f"{notes}\n\nPhong cách: {style}\n\nYêu cầu thêm: {custom_prompt}" if custom_prompt else f"{notes}\n\nPhong cách: {style}",
                        music_list=music_list,
                        additional_images=additional_images if additional_images else None
                    )
                    
                    if result:
                        st.session_state["result"] = result
                        st.session_state["results"] = []
                        
                        # Add to local history
                        st.session_state["history"].append({
                            "product_type": product_type,
                            "num_images": len(uploaded_files),
                            "output": result
                        })
                        
                        st.success(f"✅ Generate thành công! (Đã phân tích {len(uploaded_files)} ảnh)")
                        st.rerun()
                    else:
                        st.error("❌ Lỗi generate. Vui lòng thử lại!")
                else:
                    st.error(f"❌ {status}")


# ===== RIGHT COLUMN: RESULTS =====
with col_right:
    st.subheader("📤 Kết Quả")
    
    # Hiển thị kết quả
    if st.session_state.get("result"):
        result = st.session_state["result"]
        render_result_display(result)
        
        st.divider()
        
        # ===== VIDEO GENERATION SECTION =====
        st.subheader("🎬 Tạo Video Thật")
        
        if VIDEO_AVAILABLE:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                video_duration = st.selectbox("Thời lượng", [5, 8, 10], index=0)
            with col_v2:
                video_ratio = st.selectbox("Tỷ lệ", ["9:16 (TikTok)", "16:9 (YouTube)", "1:1 (Instagram)"], index=0)
            
            ratio_map = {"9:16 (TikTok)": "9:16", "16:9 (YouTube)": "16:9", "1:1 (Instagram)": "1:1"}
            
            if st.button("🎬 TẠO VIDEO VỚI VEO 3.0", type="primary", use_container_width=True):
                visual_prompt = result.get("visual_prompt", "")
                if visual_prompt:
                    with st.spinner("🎬 Đang tạo video với Veo 3.0... (có thể mất 2-5 phút)"):
                        video_gen = get_video_generator()
                        success, message, video_path = video_gen.generate_video(
                            prompt=visual_prompt,
                            aspect_ratio=ratio_map[video_ratio],
                            duration_seconds=video_duration
                        )
                        
                        if success and video_path:
                            st.session_state["video_path"] = video_path
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("Chưa có Visual Prompt. Hãy Generate Content trước.")
            
            # Hiển thị video đã tạo
            if st.session_state.get("video_path"):
                video_path = st.session_state["video_path"]
                if os.path.exists(video_path):
                    st.video(video_path)
                    with open(video_path, "rb") as f:
                        st.download_button(
                            "📥 Tải Video",
                            data=f.read(),
                            file_name=os.path.basename(video_path),
                            mime="video/mp4",
                            use_container_width=True
                        )
        else:
            st.info("💡 Cấu hình VERTEX_API_KEY trong .env để tạo video thật")
            st.caption("Hiện tại: Copy Visual Prompt → Paste vào Veo3 web")
    else:
        st.info("👆 Upload ảnh và nhấn Generate để bắt đầu")


# ===== FOOTER =====
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>🎬 Jewelry Viral Gen v1.0 | Powered by Gemini 2.5 Flash & Veo3</p>
    <p>Made with ❤️ for TikTok Affiliate Marketing</p>
</div>
""", unsafe_allow_html=True)
