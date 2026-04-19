from http.server import BaseHTTPRequestHandler
import yt_dlp
import json
import random
import time
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        video_url = query.get('url', [None])[0]
        
        if not video_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Vui lòng cung cấp URL"}).encode())
            return

        # Danh sách User-Agents ngẫu nhiên để ngụy trang
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]

        # Danh sách Proxy miễn phí (Dự phòng) - Có thể cập nhật thêm
        proxies = [
            'http://proxy.server:port', # Thay bằng proxy thật nếu có
            None # Ưu tiên chạy không proxy trước
        ]

        def get_info(url, use_proxy=False):
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'user_agent': random.choice(user_agents),
                'referer': 'https://www.google.com/',
                'impersonate': 'chrome', # Giả lập Chrome Client
                'http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            }
            if use_proxy and proxies[0]:
                ydl_opts['proxy'] = random.choice([p for p in proxies if p])

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            # Thử lần 1: Không dùng proxy để lấy tốc độ tối đa
            try:
                info = get_info(video_url)
            except Exception:
                # Thử lần 2: Đợi 1 giây và dùng Proxy dự phòng
                time.sleep(1)
                info = get_info(video_url, use_proxy=True)

            response_data = {
                'status': 'success',
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'download_url': info.get('url'),
                'duration': info.get('duration'),
                'engine': 'Vercel-Impersonate-v2'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "msg": str(e)}).encode())
