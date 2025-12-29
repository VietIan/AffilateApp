"""
UI Components cho Streamlit - Version 2.0
- Upload nhiều ảnh (cùng 1 sản phẩm)
- Bỏ giá tiền (affiliate mode)
- Thêm custom prompt
- Output tiếng Việt cho thị trường VN
"""
import streamlit as st
from typing import Dict, Optional


def render_upload_section():
    """
    Render phần upload ảnh và nhập thông tin sản phẩm
    
    Returns:
        Tuple (uploaded_files, product_type, style, notes, custom_prompt)
    """
    st.subheader("📷 Upload Ảnh Sản Phẩm")
    st.caption("💡 Có thể upload nhiều góc của CÙNG 1 sản phẩm - AI sẽ phân tích tất cả")
    
    # Upload nhiều ảnh, nhiều định dạng
    uploaded_files = st.file_uploader(
        "Chọn ảnh sản phẩm (nhiều góc = 1 sản phẩm)",
        type=["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
        accept_multiple_files=True,
        help="Upload nhiều ảnh từ nhiều góc khác nhau của CÙNG 1 sản phẩm. AI sẽ phân tích tất cả."
    )
    
    if uploaded_files:
        # Hiển thị preview các ảnh đã upload
        num_cols = min(len(uploaded_files), 4)
        cols = st.columns(num_cols)
        for idx, file in enumerate(uploaded_files[:4]):
            with cols[idx % num_cols]:
                st.image(file, caption=f"Ảnh {idx+1}", use_container_width=True)
        if len(uploaded_files) > 4:
            st.caption(f"... và {len(uploaded_files) - 4} ảnh khác")
    
    st.subheader("📝 Thông Tin Sản Phẩm")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_type = st.selectbox(
            "Loại sản phẩm",
            options=[
                "Nhẫn",
                "Nhẫn kim cương",
                "Dây chuyền",
                "Vòng tay",
                "Bông tai",
                "Đồng hồ",
                "Lắc chân",
                "Charm / Mặt dây",
                "Set trang sức",
                "Phụ kiện khác"
            ],
            index=0
        )
    
    with col2:
        style = st.selectbox(
            "Phong cách",
            options=[
                "Sang trọng / Luxury",
                "Trẻ trung / Teen",
                "Thời trang / Fashion",
                "Cổ điển / Classic",
                "Minimalist",
                "Bohemian",
                "Vintage",
                "Hiện đại / Modern"
            ],
            index=0
        )
    
    notes = st.text_area(
        "Mô tả sản phẩm (tùy chọn)",
        placeholder="VD: Nhẫn bạc đính đá CZ, thiết kế độc quyền, phù hợp làm quà tặng...",
        height=80
    )
    
    # ===== CUSTOM PROMPT SECTION =====
    st.subheader("✍️ Tùy Chỉnh Prompt (Nâng cao)")
    
    with st.expander("🔧 Tùy chỉnh Visual Prompt cho Veo3", expanded=False):
        custom_prompt = st.text_area(
            "Thêm yêu cầu riêng cho video",
            placeholder="""VD:
- Thêm hiệu ứng slow motion
- Nền màu hồng pastel
- Camera quay 360 độ
- Có tay người đeo sản phẩm
- Thêm hiệu ứng lấp lánh mạnh""",
            height=120,
            help="Các yêu cầu này sẽ được thêm vào prompt gửi cho AI"
        )
        
        st.caption("💡 Tip: Mô tả chi tiết hiệu ứng, góc quay, màu sắc bạn muốn")
    
    return uploaded_files, product_type, style, notes, custom_prompt


def render_result_display(result: Optional[Dict], image_index: int = 0):
    """
    Render phần hiển thị kết quả với nút copy
    """
    if not result:
        st.info("👆 Upload ảnh và nhấn Generate để bắt đầu")
        return
    
    # ===== VEO3 PROMPT =====
    st.subheader("🎬 Visual Prompt cho Veo3")
    visual_prompt = result.get("visual_prompt", "")
    st.text_area(
        "Copy prompt này vào Veo3",
        value=visual_prompt,
        height=150,
        label_visibility="collapsed",
        key=f"vp_{image_index}"
    )
    
    if st.button("📋 Copy Visual Prompt", key=f"copy_visual_{image_index}", use_container_width=True):
        st.session_state["clipboard"] = visual_prompt
        st.toast("✅ Đã copy Visual Prompt!")
    
    st.divider()
    
    # ===== TITLE & HOOK =====
    st.subheader("📝 Title & Hook")
    
    title = result.get("title", "")
    hook = result.get("hook", "")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Title", value=title, key=f"title_{image_index}", disabled=True)
    with col2:
        st.text_input("Hook", value=hook, key=f"hook_{image_index}", disabled=True)
    
    if st.button("📋 Copy Title + Hook", key=f"copy_title_{image_index}"):
        st.session_state["clipboard"] = f"{title}\n\n{hook}"
        st.toast("✅ Đã copy!")
    
    st.divider()
    
    # ===== HASHTAGS =====
    st.subheader("🏷️ Hashtags")
    hashtags = result.get("hashtags", [])
    hashtags_text = " ".join(hashtags)
    st.code(hashtags_text, language=None)
    
    if st.button("📋 Copy Hashtags", key=f"copy_hashtags_{image_index}"):
        st.session_state["clipboard"] = hashtags_text
        st.toast("✅ Đã copy Hashtags!")
    
    st.divider()
    
    # ===== MUSIC =====
    st.subheader("🎵 Nhạc Đề Xuất")
    music = result.get("music", {})
    
    st.success(f"🎵 **{music.get('name', 'N/A')}**")
    st.caption(f"💡 {music.get('reason', 'Phù hợp với phong cách sản phẩm')}")
    
    st.divider()
    
    # ===== CAPTION =====
    st.subheader("📋 Caption Đầy Đủ")
    caption = result.get("caption", "")
    st.text_area("Caption", value=caption, height=100, disabled=True, label_visibility="collapsed", key=f"cap_{image_index}")
    
    if st.button("📋 Copy Caption", key=f"copy_caption_{image_index}"):
        st.session_state["clipboard"] = caption
        st.toast("✅ Đã copy Caption!")
    
    st.divider()
    
    # ===== COPY ALL =====
    if st.button("📦 COPY TẤT CẢ", type="primary", use_container_width=True, key=f"copy_all_{image_index}"):
        full_content = f"""🎬 VEO3 PROMPT:
{visual_prompt}

📝 TITLE: {title}

🎣 HOOK: {hook}

🏷️ HASHTAGS: {hashtags_text}

🎵 NHẠC: {music.get('name', 'N/A')}

📋 CAPTION:
{caption}
"""
        st.session_state["clipboard"] = full_content
        st.toast("✅ Đã copy tất cả nội dung!")
        
        with st.expander("📄 Xem nội dung đã copy"):
            st.code(full_content, language=None)


def render_history_sidebar(history: list):
    """
    Render sidebar với lịch sử generate
    """
    st.sidebar.subheader("📜 Lịch Sử Gần Đây")
    
    if not history:
        st.sidebar.info("Chưa có lịch sử")
        return
    
    for i, item in enumerate(reversed(history[:5])):
        with st.sidebar.expander(f"#{i+1}: {item.get('product_type', 'Unknown')[:20]}"):
            st.write(f"⏰ {item.get('timestamp', 'Vừa xong')[:10] if item.get('timestamp') else 'Vừa xong'}")
            output = item.get('output', {})
            st.write(f"🎵 {output.get('music', {}).get('name', 'N/A')}")
            if st.button(f"Load #{i+1}", key=f"load_{i}"):
                st.session_state["result"] = output


def render_music_status(music_data: dict):
    """
    Render trạng thái nhạc trending
    """
    if not music_data:
        st.sidebar.warning("⚠️ Chưa có dữ liệu nhạc")
        return
    
    last_updated = music_data.get("last_updated", "N/A")
    songs_count = len(music_data.get("songs", []))
    
    st.sidebar.success(f"🎵 {songs_count} bài hát trending")
    st.sidebar.caption(f"Cập nhật: {last_updated[:10] if len(last_updated) > 10 else last_updated}")
