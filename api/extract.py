from http.server import BaseHTTPRequestHandler
import yt_dlp
import json
import random
import urllib.request
import time
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def fetch_fresh_proxies(self):
        """Tự động quét lấy Proxy Elite mới nhất từ vệ tinh"""
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
            self.wfile.write(json.dumps({"error": "Missing URL"}).encode())
            return

        # DANH SÁCH 10 PROXY ELITE DỰ PHÒNG CỨNG
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
                # CHIẾN THUẬT ANDROID BYPASS
                'impersonate': 'android', 
                'extractor_args': {'youtube': {'player_client': ['android']}},
                'user_agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Build/UQ1A.240205.002) gzip(gfe)',
                'referer': 'https://www.google.com/',
                'http_headers': {
                    'X-YouTube-Client-Name': '3',
                    'X-YouTube-Client-Version': '19.05.36',
                }
            }
            if proxy:
                ydl_opts['proxy'] = proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            info = None
            # THỬ LẦN 1: IP VERCEL VỚI ANDROID HEADERS
            try:
                info = get_info(video_url)
            except:
                # THỬ LẦN 2: XOAY VÒNG PROXY ELITE
                random.shuffle(elite_proxies)
                for p in elite_proxies[:3]:
                    try:
                        info = get_info(video_url, proxy=p)
                        if info: break
                    except: continue
                
                # THỬ LẦN 3: FETCH PROXY MỚI TỪ CLOUD
                if not info:
                    fresh = self.fetch_fresh_proxies()
                    if fresh:
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
                'method': 'Android-Client-Impersonation'
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
