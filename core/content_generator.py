"""
Content Generator
Orchestrator kết hợp Gemini + Prompt Engine + Music để generate content hoàn chỉnh
"""
import json
from typing import Dict, List, Optional
from .gemini_client import GeminiClient
from .prompt_engine import PromptEngine, get_system_prompt


class ContentGenerator:
    def __init__(self):
        self.gemini = GeminiClient()
        self.prompt_engine = PromptEngine()
    
    def generate(
        self,
        image_data: bytes,
        product_type: str,
        price: str = "",
        notes: str = "",
        music_list: List[Dict] = None,
        additional_images: List[bytes] = None
    ) -> Optional[Dict]:
        """
        Generate trọn bộ content cho video TikTok
        
        Args:
            image_data: Bytes của ảnh sản phẩm chính
            product_type: Loại sản phẩm (Nhẫn, Dây chuyền, etc.)
            price: Giá sản phẩm (không dùng cho affiliate)
            notes: Ghi chú thêm + phong cách
            music_list: Danh sách nhạc trending
            additional_images: List các ảnh phụ của cùng 1 sản phẩm
            
        Returns:
            Dict với visual_prompt, title, hook, hashtags, music, caption
        """
        # Chuẩn bị product info
        product_info = {
            "type": product_type,
            "price": price,
            "notes": notes
        }
        
        # Lấy system prompt tùy chỉnh theo loại sản phẩm
        system_prompt = self.prompt_engine.get_full_prompt(product_info)
        
        # Music list mặc định nếu không có
        if not music_list:
            music_list = self._get_default_music()
        
        # Gọi Gemini để generate (hỗ trợ nhiều ảnh = 1 sản phẩm)
        result = self.gemini.generate_viral_content(
            image_data=image_data,
            product_info=product_info,
            music_list=music_list,
            system_prompt=system_prompt,
            additional_images=additional_images
        )
        
        if result:
            # Thêm metadata
            result["_metadata"] = {
                "product_type": product_type,
                "num_images": 1 + (len(additional_images) if additional_images else 0),
                "category": self.prompt_engine.get_category(product_type, price)
            }
        
        return result
    
    def _get_default_music(self) -> List[Dict]:
        """Danh sách nhạc mặc định khi không có data"""
        return [
            {"name": "APT", "artist": "ROSÉ & Bruno Mars", "vibe": ["Sang chảnh", "Trendy"]},
            {"name": "Die With A Smile", "artist": "Lady Gaga", "vibe": ["Lãng mạn", "Ballad"]},
            {"name": "Cắt Đôi Nỗi Sầu", "artist": "Tăng Duy Tân", "vibe": ["Sôi động", "Remix"]},
            {"name": "Piano Nhẹ Nhàng", "artist": "Instrumental", "vibe": ["Sang trọng", "Nhẹ nhàng"]},
        ]
    
    def format_output(self, result: Dict) -> str:
        """Format kết quả thành text đẹp để copy"""
        if not result:
            return "Không có kết quả"
        
        output = []
        output.append("=" * 50)
        output.append("🎬 VEO3 VISUAL PROMPT")
        output.append("=" * 50)
        output.append(result.get("visual_prompt", ""))
        output.append("")
        
        output.append("=" * 50)
        output.append("📝 TITLE & HOOK")
        output.append("=" * 50)
        output.append(f"Title: {result.get('title', '')}")
        output.append(f"Hook: {result.get('hook', '')}")
        output.append("")
        
        output.append("=" * 50)
        output.append("🏷️ HASHTAGS")
        output.append("=" * 50)
        hashtags = result.get("hashtags", [])
        output.append(" ".join(hashtags))
        output.append("")
        
        output.append("=" * 50)
        output.append("🎵 MUSIC")
        output.append("=" * 50)
        music = result.get("music", {})
        output.append(f"Bài hát: {music.get('name', 'N/A')}")
        output.append(f"Lý do: {music.get('reason', 'N/A')}")
        output.append("")
        
        output.append("=" * 50)
        output.append("📋 CAPTION ĐẦY ĐỦ")
        output.append("=" * 50)
        output.append(result.get("caption", ""))
        
        return "\n".join(output)
    
    def test_connection(self) -> bool:
        """Test kết nối với Gemini"""
        return self.gemini.test_connection()
