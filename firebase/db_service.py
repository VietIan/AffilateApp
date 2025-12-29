"""
Firebase Database Service
CRUD operations cho Realtime Database
"""
import pyrebase
from datetime import datetime
from .config import get_firebase_config


class FirebaseDB:
    def __init__(self):
        config = get_firebase_config()
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
    
    # ============ MUSIC TRENDING ============
    def get_music_trending(self):
        """Lấy danh sách nhạc trending từ Firebase"""
        try:
            data = self.db.child("music_trending").get()
            if data.val():
                return data.val()
            return None
        except Exception as e:
            print(f"Error getting music trending: {e}")
            return None
    
    def update_music_trending(self, songs: list):
        """Cập nhật danh sách nhạc trending"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "source": "tiktok_scraper",
                "songs": songs
            }
            self.db.child("music_trending").set(data)
            return True
        except Exception as e:
            print(f"Error updating music trending: {e}")
            return False
    
    def is_music_cache_valid(self, max_hours=24):
        """Kiểm tra cache nhạc còn hợp lệ không"""
        try:
            data = self.db.child("music_trending").child("last_updated").get()
            if data.val():
                last_updated = datetime.fromisoformat(data.val())
                hours_diff = (datetime.now() - last_updated).total_seconds() / 3600
                return hours_diff < max_hours
            return False
        except:
            return False
    
    # ============ GENERATION HISTORY ============
    def save_generation(self, data: dict):
        """Lưu lịch sử generate content"""
        try:
            generation = {
                "timestamp": datetime.now().isoformat(),
                "product_type": data.get("product_type", "unknown"),
                "price": data.get("price", ""),
                "notes": data.get("notes", ""),
                "output": data.get("output", {}),
                "status": "completed"
            }
            result = self.db.child("generation_history").push(generation)
            return result.get("name", None)
        except Exception as e:
            print(f"Error saving generation: {e}")
            return None
    
    def get_generation_history(self, limit=20):
        """Lấy lịch sử generate gần đây"""
        try:
            data = self.db.child("generation_history").order_by_child("timestamp").limit_to_last(limit).get()
            if data.val():
                return list(data.val().values())
            return []
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    # ============ POST HISTORY ============
    def save_post(self, generation_id: str, platform: str, video_url: str):
        """Lưu lịch sử đăng video"""
        try:
            post = {
                "generation_id": generation_id,
                "posted_at": datetime.now().isoformat(),
                "platform": platform,
                "video_url": video_url,
                "metrics": {
                    "views": 0,
                    "likes": 0,
                    "comments": 0
                }
            }
            self.db.child("post_history").push(post)
            return True
        except Exception as e:
            print(f"Error saving post: {e}")
            return False
    
    # ============ PROMPT TEMPLATES ============
    def get_prompt_templates(self):
        """Lấy prompt templates đã lưu"""
        try:
            data = self.db.child("prompt_templates").get()
            if data.val():
                return data.val()
            return {}
        except:
            return {}
    
    def save_prompt_template(self, name: str, template: dict):
        """Lưu prompt template mới"""
        try:
            self.db.child("prompt_templates").child(name).set(template)
            return True
        except:
            return False
