"""
Image Processor
Xử lý và validate ảnh trước khi gửi lên Gemini
"""
from PIL import Image
import io
from typing import Tuple, Optional


class ImageProcessor:
    # Kích thước tối đa cho Gemini (để tiết kiệm token)
    MAX_WIDTH = 1024
    MAX_HEIGHT = 1024
    MAX_SIZE_MB = 4
    
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP', 'GIF']
    
    @staticmethod
    def validate_image(image_data: bytes) -> Tuple[bool, str]:
        """
        Validate ảnh trước khi xử lý
        
        Returns:
            Tuple (is_valid, message)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in ImageProcessor.SUPPORTED_FORMATS:
                return False, f"Format không hỗ trợ: {image.format}. Chỉ chấp nhận: {', '.join(ImageProcessor.SUPPORTED_FORMATS)}"
            
            # Check size
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb > ImageProcessor.MAX_SIZE_MB:
                return False, f"Ảnh quá lớn: {size_mb:.1f}MB. Tối đa: {ImageProcessor.MAX_SIZE_MB}MB"
            
            # Check dimensions (tối thiểu 100x100)
            if image.width < 100 or image.height < 100:
                return False, f"Ảnh quá nhỏ: {image.width}x{image.height}. Tối thiểu: 100x100"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Lỗi đọc ảnh: {str(e)}"
    
    @staticmethod
    def resize_if_needed(image_data: bytes) -> bytes:
        """
        Resize ảnh nếu quá lớn để tiết kiệm token Gemini
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check nếu cần resize
            if image.width <= ImageProcessor.MAX_WIDTH and image.height <= ImageProcessor.MAX_HEIGHT:
                return image_data
            
            # Tính ratio để giữ tỷ lệ
            ratio = min(
                ImageProcessor.MAX_WIDTH / image.width,
                ImageProcessor.MAX_HEIGHT / image.height
            )
            
            new_size = (int(image.width * ratio), int(image.height * ratio))
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert sang bytes
            buffer = io.BytesIO()
            format = image.format or 'JPEG'
            resized.save(buffer, format=format, quality=85)
            
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Lỗi resize: {e}")
            return image_data
    
    @staticmethod
    def get_image_info(image_data: bytes) -> Optional[dict]:
        """
        Lấy thông tin về ảnh
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_kb": len(image_data) / 1024
            }
        except:
            return None
    
    @staticmethod
    def process_for_gemini(image_data: bytes) -> Tuple[Optional[bytes], str]:
        """
        Pipeline xử lý ảnh hoàn chỉnh cho Gemini
        
        Returns:
            Tuple (processed_image_bytes, status_message)
        """
        # Validate
        is_valid, msg = ImageProcessor.validate_image(image_data)
        if not is_valid:
            return None, msg
        
        # Resize nếu cần
        processed = ImageProcessor.resize_if_needed(image_data)
        
        # Lấy info
        info = ImageProcessor.get_image_info(processed)
        if info:
            status = f"✅ Ảnh OK: {info['width']}x{info['height']} | {info['size_kb']:.0f}KB | {info['format']}"
        else:
            status = "✅ Ảnh đã xử lý"
        
        return processed, status
