import yt_dlp
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        video_url = params.get('url', [None])[0]
        mode = params.get('mode', ['video'])[0] # video hoặc audio

        if not video_url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No URL provided"}).encode())
            return

        # Cấu hình tối ưu để lấy link raw nhanh nhất
        ydl_opts = {
            'format': 'bestaudio/best' if mode == 'audio' else 'bestvideo+bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                # Lọc dữ liệu quan trọng để website xử lý
                data = {
                    "status": "success",
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "links": [
                        {"quality": f.get("format_note"), "url": f.get("url"), "ext": f.get("ext")}
                        for f in info.get("formats", []) if f.get("url")
                    ]
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*') # Cho phép website của bạn gọi tới
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "msg": str(e)}).encode())