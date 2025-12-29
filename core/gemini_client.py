"""
Gemini Client
Kết nối với Gemini 2.5 Flash để phân tích ảnh và generate content
"""
import os
import json
import base64
from typing import Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(self.model_name)
        
    def analyze_image(self, image_data: bytes, prompt: str) -> Optional[str]:
        """
        Phân tích ảnh với Gemini Vision
        
        Args:
            image_data: Bytes của ảnh
            prompt: Prompt để gửi cùng ảnh
            
        Returns:
            Response text từ Gemini
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Gọi Gemini với ảnh
            response = self.model.generate_content([prompt, image])
            
            return response.text
            
        except Exception as e:
            print(f"❌ Lỗi Gemini: {e}")
            return None
    
    def generate_content(self, prompt: str) -> Optional[str]:
        """
        Generate content chỉ với text (không có ảnh)
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Lỗi Gemini: {e}")
            return None
    
    def generate_viral_content(
        self, 
        image_data: bytes, 
        product_info: Dict,
        music_list: list,
        system_prompt: str,
        additional_images: list = None
    ) -> Optional[Dict]:
        """
        Generate nội dung viral cho TikTok từ ảnh sản phẩm
        
        Args:
            image_data: Bytes của ảnh sản phẩm chính
            product_info: Dict chứa thông tin sản phẩm (type, price, notes)
            music_list: Danh sách nhạc trending để AI chọn
            system_prompt: System instruction cho AI
            additional_images: List các ảnh phụ (bytes) của cùng 1 sản phẩm
            
        Returns:
            Dict chứa visual_prompt, title, hook, hashtags, music
        """
        try:
            # Tạo list tất cả ảnh (nhiều góc của 1 sản phẩm)
            images = [Image.open(io.BytesIO(image_data))]
            
            if additional_images:
                for img_bytes in additional_images:
                    try:
                        images.append(Image.open(io.BytesIO(img_bytes)))
                    except:
                        continue
            
            num_images = len(images)
            
            # Tạo prompt đầy đủ - TIẾNG VIỆT
            full_prompt = f"""
{system_prompt}

=== THÔNG TIN SẢN PHẨM ===
- Loại: {product_info.get('type', 'Trang sức')}
- Ghi chú: {product_info.get('notes', 'Không có')}
- Số ảnh: {num_images} ảnh (các góc khác nhau của CÙNG 1 sản phẩm)

=== DANH SÁCH NHẠC TRENDING VIỆT NAM ===
{json.dumps(music_list, indent=2, ensure_ascii=False)}

=== YÊU CẦU ===
Phân tích TẤT CẢ {num_images} ảnh (đây là các góc khác nhau của CÙNG 1 sản phẩm).
Tạo NỘI DUNG TIẾNG VIỆT cho thị trường Việt Nam.

Trả về JSON với format sau:
{{
    "visual_prompt": "Prompt TIẾNG VIỆT mô tả video cho Veo3. Bao gồm: góc quay, ánh sáng, chuyển động camera, hiệu ứng, mood. Dài 50-100 từ. VD: Quay cận cảnh nhẫn kim cương trên nền nhung đen, ánh sáng studio 3 điểm với rim light làm nổi bật viền platinum, hiệu ứng lấp lánh trên các mặt cắt kim cương, camera quay chậm xoay 360 độ, chất lượng 4K điện ảnh, không khí sang trọng lãng mạn",
    "title": "Tiêu đề viral tiếng Việt có emoji, gây tò mò, dưới 50 ký tự",
    "hook": "Câu hook đầu video tiếng Việt, dưới 10 từ, gây sốc hoặc tò mò",
    "hashtags": ["#hashtag1", "#hashtag2", "...tối đa 10 hashtags tiếng Việt"],
    "music": {{
        "name": "Tên bài hát phù hợp nhất từ danh sách",
        "reason": "Lý do chọn bài này (tiếng Việt)"
    }},
    "caption": "Caption đầy đủ tiếng Việt cho video TikTok, bao gồm mô tả sản phẩm và call-to-action"
}}

CHỈ TRẢ VỀ JSON, KHÔNG CÓ TEXT KHÁC.
"""
            
            # Gửi tất cả ảnh cùng prompt
            content_parts = [full_prompt] + images
            response = self.model.generate_content(content_parts)
            response_text = response.text.strip()
            
            # Parse JSON từ response
            # Xử lý trường hợp Gemini wrap trong ```json ... ```
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi parse JSON: {e}")
            print(f"Response: {response_text[:500]}")
            return None
        except Exception as e:
            print(f"❌ Lỗi generate content: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test kết nối với Gemini API"""
        try:
            response = self.model.generate_content("Say 'OK' if you can hear me")
            return "OK" in response.text.upper()
        except Exception as e:
            print(f"❌ Lỗi kết nối Gemini: {e}")
            return False
