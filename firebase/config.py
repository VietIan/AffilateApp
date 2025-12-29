"""
Firebase Configuration
Sử dụng Pyrebase4 để kết nối với Firebase Realtime Database
"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_firebase_config():
    """Trả về config cho Firebase"""
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    }
