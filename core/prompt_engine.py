"""
Prompt Engine
System prompts và templates cho 3 modules: Visual, Copywriting, DJ
"""

# ============================================================
# MASTER SYSTEM PROMPT - Dạy AI tư duy như TikToker chuyên nghiệp
# ============================================================

SYSTEM_PROMPT = """
Bạn là một chuyên gia TikTok Affiliate Marketing chuyên về ngành trang sức (Jewelry).
Nhiệm vụ: Phân tích ảnh sản phẩm và tạo trọn bộ nguyên liệu làm video TikTok viral.

=== MODULE 1: VISUAL DIRECTOR (Cho Veo3 AI Video) ===

Quy tắc tạo Visual Prompt:
1. LUÔN dùng tiếng Anh, chuẩn điện ảnh Hollywood
2. Bắt buộc có: "Studio lighting", "Rim light" (ánh sáng viền làm nổi kim loại)
3. Bắt buộc có: "Macro shot" hoặc "Close-up" để thấy chi tiết đá/kim cương
4. Thêm camera movement: "Slow dolly in", "Orbit shot", "Crane shot"
5. Thêm hiệu ứng: "Sparkle effects", "Light flares", "Bokeh background"
6. Độ dài: 50-100 từ tiếng Anh

Template Visual Prompt:
"[Camera angle] of [product description], [lighting setup], [background], [special effects], [camera movement], cinematic 4K, [mood/atmosphere]"

Ví dụ cho nhẫn kim cương:
"Extreme macro shot of diamond engagement ring on black velvet, studio three-point lighting with dramatic rim light highlighting platinum band, shallow depth of field with bokeh, brilliant sparkle effects on diamond facets, slow orbit camera movement, cinematic 4K, luxurious and romantic atmosphere"

=== MODULE 2: COPYWRITING MASTER (Cho Viewer) ===

Quy tắc viết Hook:
1. DƯỚI 10 TỪ, gây sốc hoặc tò mò
2. Dùng các pattern viral:
   - "Đừng [hành động] nếu [điều kiện]..." 
   - "POV: Bạn là [nhân vật]..."
   - "[Số tiền] mua được [cảm xúc]..."
   - "Ai cho phép [đối tượng] đẹp thế này?"

Quy tắc viết Title:
1. Dưới 50 ký tự
2. Có emoji phù hợp
3. Gợi tò mò, không spoil hết

Quy tắc Hashtags:
1. Mix: 3 hashtag viral + 3 hashtag ngách + 4 hashtag sản phẩm
2. Hashtag viral: #tiktokviral #fyp #xuhuong #trending
3. Hashtag ngách: #jewelry #trangsuc #phukien #trangsucdep
4. Hashtag sản phẩm: dựa trên loại SP (nhẫn, dây chuyền, vòng tay...)

=== MODULE 3: DJ SELECTOR (Cho Nhạc) ===

Quy trình chọn nhạc:
1. Nhìn ảnh → Xác định MOOD (Sang trọng? Trẻ trung? Lãng mạn?)
2. Xác định TARGET AUDIENCE (Teen? Trung niên? Cao cấp?)
3. Đối chiếu với danh sách nhạc trending
4. Chọn bài có VIBE phù hợp nhất

Mapping Mood → Vibe:
- Sản phẩm Luxury (Kim cương, Vàng cao cấp) → Nhạc sang trọng, nhẹ nhàng, piano
- Sản phẩm Teen (Vòng tay hạt, Màu sắc) → Nhạc remix, sôi động, trendy
- Sản phẩm Classic (Vàng truyền thống) → Nhạc ballad, cảm xúc, bolero
- Sản phẩm Thời trang (Bông tai, Phụ kiện) → Nhạc biến hình, thời trang, catwalk

=== OUTPUT FORMAT ===
Luôn trả về JSON hợp lệ, không có text thừa.
"""


# ============================================================
# PROMPT TEMPLATES CHO TỪNG LOẠI SẢN PHẨM
# ============================================================

PRODUCT_TEMPLATES = {
    "luxury": {
        "visual_keywords": [
            "luxury", "elegant", "premium", "sophisticated",
            "diamond sparkle", "gold shimmer", "platinum shine"
        ],
        "lighting": "three-point studio lighting with dramatic rim light",
        "mood": "luxurious, romantic, exclusive",
        "music_vibe": ["Sang trọng", "Nhẹ nhàng", "Piano", "Ballad"],
        "hook_patterns": [
            "Đừng tặng cái này nếu chưa sẵn sàng...",
            "{price} không mua được tình yêu, nhưng...",
            "Ai cho phép viên kim cương này đẹp thế?",
        ]
    },
    
    "teen": {
        "visual_keywords": [
            "colorful", "vibrant", "playful", "trendy",
            "pastel", "kawaii", "aesthetic"
        ],
        "lighting": "bright soft lighting with colorful accents",
        "mood": "fun, energetic, youthful",
        "music_vibe": ["Sôi động", "Remix", "Nhảy", "Trendy"],
        "hook_patterns": [
            "POV: Crush thấy bạn đeo cái này",
            "Under 200k mà xinh quá trời!",
            "Đừng để bạn thân thấy video này...",
        ]
    },
    
    "classic": {
        "visual_keywords": [
            "timeless", "traditional", "heritage", "elegant",
            "gold", "classic design"
        ],
        "lighting": "warm golden hour lighting",
        "mood": "warm, nostalgic, precious",
        "music_vibe": ["Cảm xúc", "Ballad", "Nhẹ nhàng"],
        "hook_patterns": [
            "Mẹ nhìn thấy cái này chắc khóc...",
            "Vàng ta hay vàng tây? Câu trả lời là...",
            "Truyền 3 đời vẫn không lỗi mốt",
        ]
    },
    
    "fashion": {
        "visual_keywords": [
            "stylish", "modern", "chic", "statement piece",
            "accessory", "outfit complement"
        ],
        "lighting": "fashion editorial lighting",
        "mood": "confident, stylish, trendsetting",
        "music_vibe": ["Thời trang", "Biến hình", "Catwalk", "Trendy"],
        "hook_patterns": [
            "Outfit 10 điểm chỉ nhờ chi tiết này",
            "Phụ kiện này cứu cả set đồ",
            "Đừng bỏ qua nếu bạn thích OOTD",
        ]
    }
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_system_prompt() -> str:
    """Trả về system prompt chính"""
    return SYSTEM_PROMPT


def get_template_for_category(category: str) -> dict:
    """Lấy template cho loại sản phẩm cụ thể"""
    return PRODUCT_TEMPLATES.get(category, PRODUCT_TEMPLATES["fashion"])


def detect_product_category(product_type: str, price: str = "") -> str:
    """
    Tự động detect category dựa trên loại SP và giá
    """
    product_lower = product_type.lower()
    
    # Parse giá
    price_value = 0
    if price:
        # Loại bỏ ký tự không phải số
        price_clean = ''.join(filter(str.isdigit, price))
        price_value = int(price_clean) if price_clean else 0
    
    # Luxury: Kim cương, giá > 10 triệu
    if any(k in product_lower for k in ['kim cương', 'diamond', 'platinum', 'bạch kim']):
        return "luxury"
    if price_value > 10000000:  # > 10 triệu
        return "luxury"
    
    # Teen: Vòng tay hạt, giá rẻ
    if any(k in product_lower for k in ['hạt', 'charm', 'teen', 'dây da']):
        return "teen"
    if price_value > 0 and price_value < 500000:  # < 500k
        return "teen"
    
    # Classic: Vàng, truyền thống
    if any(k in product_lower for k in ['vàng', 'gold', 'truyền thống', '24k', '18k']):
        return "classic"
    
    # Default: Fashion
    return "fashion"


class PromptEngine:
    """Engine để generate prompts tùy chỉnh"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.templates = PRODUCT_TEMPLATES
    
    def get_full_prompt(self, product_info: dict) -> str:
        """Tạo prompt đầy đủ cho một sản phẩm"""
        category = detect_product_category(
            product_info.get('type', ''),
            product_info.get('price', '')
        )
        template = self.templates.get(category, self.templates["fashion"])
        
        enhanced_prompt = f"""
{self.system_prompt}

=== GỢI Ý CHO SẢN PHẨM NÀY ===
Category detected: {category.upper()}
Visual keywords gợi ý: {', '.join(template['visual_keywords'])}
Lighting gợi ý: {template['lighting']}
Mood gợi ý: {template['mood']}
Music vibe phù hợp: {', '.join(template['music_vibe'])}

Hook patterns hay cho loại này:
{chr(10).join(f'- {h}' for h in template['hook_patterns'])}
"""
        return enhanced_prompt
    
    def get_category(self, product_type: str, price: str = "") -> str:
        """Wrapper cho detect_product_category"""
        return detect_product_category(product_type, price)
