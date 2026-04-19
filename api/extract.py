from http.server import BaseHTTPRequestHandler
import yt_dlp
import json
import random
import urllib.request
import time
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def fetch_fresh_proxies(self):
        """Tự động lấy danh sách Proxy mới nhất để dự phòng"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite"
            with urllib.request.urlopen(url) as response:
                proxies = response.read().decode().splitlines()
                return ["http://" + p for p in proxies if p]
        except:
            return []

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        video_url = query.get('url', [None])[0]
        
        if not video_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Vui lòng cung cấp URL"}).encode())
            return

        # 1. KHO USER-AGENT ĐA NỀN TẢNG
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        ]

        # 2. DANH SÁCH 10 PROXY ELITE CỐ ĐỊNH
        elite_proxies = [
            'http://161.35.70.244:80', 'http://159.203.185.12:3128', 
            'http://167.172.186.10:80', 'http://138.197.148.215:80',
            'http://188.166.216.21:3128', 'http://64.227.14.131:80',
            'http://206.189.155.244:80', 'http://134.209.29.120:8080',
            'http://178.128.113.118:3128', 'http://159.65.245.243:80'
        ]

        def get_info(url, proxy=None):
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'impersonate': 'chrome',
                'user_agent': random.choice(user_agents),
                'referer': 'https://www.google.com/',
                'http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            }
            if proxy:
                ydl_opts['proxy'] = proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            info = None
            # BƯỚC 1: THỬ IP SẠCH VERCEL
            try:
                info = get_info(video_url)
            except:
                # BƯỚC 2: THỬ DANH SÁCH ELITE CỐ ĐỊNH
                random.shuffle(elite_proxies)
                for p in elite_proxies[:3]:
                    try:
                        info = get_info(video_url, proxy=p)
                        if info: break
                    except: continue
                
                # BƯỚC 3: THỬ QUÉT PROXY MỚI NẾU VẪN LỖI
                if not info:
                    fresh = self.fetch_fresh_proxies()
                    random.shuffle(fresh)
                    for p in fresh[:5]:
                        try:
                            info = get_info(video_url, proxy=p)
                            if info: break
                        except: continue

            if not info:
                raise Exception("YouTube chặn quá mạnh. Hãy thử lại sau 30 giây.")

            response_data = {
                'status': 'success',
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'download_url': info.get('url'),
                'res': info.get('resolution'),
                'mode': 'Triple-Layer-Bypass'
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
