"""
TikTok CSS Selectors
Các selector để scrape dữ liệu từ TikTok
"""

# Video Info Selectors
TIKTOK_SELECTORS = {
    # Meta info
    "video_url": 'meta[property="og:url"]',
    "description": 'span.css-j2a19r-SpanText',
    "music_title": '.css-pvx3oa-DivMusicText',
    "upload_date": 'span[data-e2e="browser-nickname"] span:last-child',
    "tags": '[data-e2e="search-common-link"]',
    
    # Engagement Metrics
    "views": '[data-e2e="video-views"]',
    "likes": '[data-e2e="like-count"]',
    "comments": '[data-e2e="comment-count"]',
    "shares": '[data-e2e="share-count"]',
    "bookmarks": '[data-e2e="undefined-count"]',
    
    # Author info
    "author": '[data-e2e="browser-username"]',
}

# TikTok Creative Center Selectors (for trending music)
CREATIVE_CENTER_SELECTORS = {
    # Music list page
    "music_card": '[class*="CardContainer"]',
    "song_name": '[class*="MusicName"]',
    "artist_name": '[class*="AuthorName"]',
    "usage_count": '[class*="VideoCount"]',
    "music_link": '[class*="MusicLink"]',
    
    # Alternative selectors (TikTok thường xuyên thay đổi class)
    "music_item_alt": '.music-item',
    "song_name_alt": '.song-title',
    "artist_alt": '.artist-name',
}

# Search page selectors
SEARCH_SELECTORS = {
    "search_input": '[data-e2e="search-user-input"]',
    "search_button": '[data-e2e="search-button"]',
    "video_card": '[data-e2e="search-card-desc"]',
}
