import time
import cv2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class VideoHandler(BaseHTTPRequestHandler):
    def __init__(self, capture):
        self.capture = capture
    def Get(self):
        print self.path
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    rc, img = self.capture.read()
                    if not rc:
                        continue
                    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    r, buf = cv2.imencode(".jpg", imgRGB)
                    self.wfile.write("--jpgboundary\r\n")
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(buf)))
                    self.end_headers()
                    self.wfile.write(bytearray(buf))
                    self.wfile.write('\r\n')
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html') or self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="http://127.0.0.1:9090/cam.mjpg"/>')
            self.wfile.write('</body></html>')
            return

