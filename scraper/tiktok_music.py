"""
TikTok Music Scraper
Scrape nhạc trending từ TikTok Creative Center hoặc video
"""
import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from .selectors import TIKTOK_SELECTORS, CREATIVE_CENTER_SELECTORS


class TikTokMusicScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.timeout = 30000
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
    async def _init_browser(self):
        """Khởi tạo browser với Playwright"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.user_agent,
        )
        return playwright, browser, context
    
    async def scrape_trending_music(self, limit: int = 10) -> List[Dict]:
        """
        Scrape nhạc trending từ TikTok Creative Center
        URL: https://ads.tiktok.com/business/creativecenter/music/pc/en
        """
        url = "https://ads.tiktok.com/business/creativecenter/music/pc/en"
        songs = []
        
        try:
            playwright, browser, context = await self._init_browser()
            page = await context.new_page()
            
            print(f"🎵 Đang truy cập TikTok Creative Center...")
            await page.goto(url, wait_until="networkidle", timeout=self.timeout)
            await asyncio.sleep(3)  # Đợi page load hoàn toàn
            
            # Scroll để load thêm music
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(1)
            
            # Thử scrape với nhiều selector khác nhau
            music_items = await page.query_selector_all('[class*="musicCard"]') or \
                         await page.query_selector_all('[class*="CardContainer"]') or \
                         await page.query_selector_all('.music-item')
            
            print(f"📀 Tìm thấy {len(music_items)} bài hát")
            
            for i, item in enumerate(music_items[:limit]):
                try:
                    # Lấy tên bài hát
                    name_el = await item.query_selector('[class*="MusicName"]') or \
                             await item.query_selector('[class*="song"]') or \
                             await item.query_selector('span')
                    name = await name_el.inner_text() if name_el else f"Song {i+1}"
                    
                    # Lấy tên artist
                    artist_el = await item.query_selector('[class*="Author"]') or \
                               await item.query_selector('[class*="artist"]')
                    artist = await artist_el.inner_text() if artist_el else "Unknown"
                    
                    # Lấy số lượng video sử dụng
                    count_el = await item.query_selector('[class*="VideoCount"]') or \
                              await item.query_selector('[class*="count"]')
                    usage = await count_el.inner_text() if count_el else "0"
                    
                    song = {
                        "id": f"song_{i+1:03d}",
                        "name": name.strip(),
                        "artist": artist.strip(),
                        "usage_count": usage.strip(),
                        "vibe": self._analyze_vibe(name),
                        "scraped_at": datetime.now().isoformat()
                    }
                    songs.append(song)
                    print(f"  ✅ {name} - {artist}")
                    
                except Exception as e:
                    print(f"  ❌ Lỗi scrape item {i}: {e}")
                    continue
            
            await browser.close()
            await playwright.stop()
            
        except Exception as e:
            print(f"❌ Lỗi scrape Creative Center: {e}")
            # Fallback: đọc từ cache local
            songs = self._load_cache()
        
        return songs
    
    async def scrape_video_music(self, video_url: str) -> Optional[Dict]:
        """
        Scrape thông tin nhạc từ một video TikTok cụ thể
        """
        try:
            playwright, browser, context = await self._init_browser()
            page = await context.new_page()
            
            print(f"🎬 Đang scrape video: {video_url}")
            await page.goto(video_url, wait_until="networkidle", timeout=self.timeout)
            await asyncio.sleep(2)
            
            # Lấy thông tin nhạc
            music_el = await page.query_selector(TIKTOK_SELECTORS["music_title"])
            music_title = await music_el.inner_text() if music_el else None
            
            # Lấy metrics
            views_el = await page.query_selector(TIKTOK_SELECTORS["views"])
            likes_el = await page.query_selector(TIKTOK_SELECTORS["likes"])
            
            result = {
                "music_title": music_title,
                "views": await views_el.inner_text() if views_el else "0",
                "likes": await likes_el.inner_text() if likes_el else "0",
                "video_url": video_url,
                "scraped_at": datetime.now().isoformat()
            }
            
            await browser.close()
            await playwright.stop()
            
            return result
            
        except Exception as e:
            print(f"❌ Lỗi scrape video: {e}")
            return None
    
    def _analyze_vibe(self, song_name: str) -> List[str]:
        """Phân tích vibe của bài hát dựa trên tên"""
        vibes = []
        name_lower = song_name.lower()
        
        # Keyword mapping
        if any(k in name_lower for k in ['remix', 'dance', 'edm', 'drop']):
            vibes.extend(['Sôi động', 'Remix', 'Nhảy'])
        if any(k in name_lower for k in ['love', 'tình', 'yêu', 'heart']):
            vibes.extend(['Lãng mạn', 'Cảm xúc'])
        if any(k in name_lower for k in ['piano', 'acoustic', 'nhẹ']):
            vibes.extend(['Nhẹ nhàng', 'Sang trọng'])
        if any(k in name_lower for k in ['trending', 'hot', 'viral']):
            vibes.extend(['Trendy', 'Viral'])
        
        # Default vibe nếu không detect được
        if not vibes:
            vibes = ['Trendy', 'Phổ biến']
        
        return list(set(vibes))
    
    def _load_cache(self) -> List[Dict]:
        """Load nhạc từ cache local khi scrape fail"""
        cache_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'music_cache.json')
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_to_cache(self, songs: List[Dict]):
        """Lưu nhạc vào cache local"""
        cache_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'music_cache.json')
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(songs, f, indent=2, ensure_ascii=False)
            print(f"💾 Đã lưu {len(songs)} bài vào cache")
        except Exception as e:
            print(f"❌ Lỗi lưu cache: {e}")


# Sync wrapper để dùng trong Streamlit
def scrape_trending_music_sync(limit: int = 10) -> List[Dict]:
    """Sync wrapper cho async scraper"""
    scraper = TikTokMusicScraper(headless=True)
    return asyncio.run(scraper.scrape_trending_music(limit))


def scrape_video_music_sync(video_url: str) -> Optional[Dict]:
    """Sync wrapper cho async video scraper"""
    scraper = TikTokMusicScraper(headless=True)
    return asyncio.run(scraper.scrape_video_music(video_url))
