# Name: stream.py
# Author: Vieux Adriano
# Date: 05.05.2023
# Project: Travail de Bachelor - Détection d'hydrocarbure sur route
# Script permettant de diffuser sur une page locale les images de la caméra
import io
import logging
import socketserver
from threading import Condition
from http import server
from libcamera import controls


from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder, Quality
from picamera2.outputs import FileOutput

PAGE="""\
    <html>
    <head>
    <title>Detection hydrocabures - Retour video</title>
    </head>
    <body>
    <center><h1>Detection hydrocarbures - Retour video</h1></center>
    <center><img src= "stream.mjpg" width="900" height="640"></center>
    </body>
    </html>
    """
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        #self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age',0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


with Picamera2() as picam2:
    #picam2.configure(picam2.create_video_configuration(main={"size": (1332,990)}))
    picam2.configure(picam2.create_video_configuration())

    output = StreamingOutput()
    #camera.rotation = 90
    distance =0.90#[m] #picamera2 doc chap 5.2.3
    picam2.set_controls({"ExposureTime":1000, "AfMode": controls.AfModeEnum.Manual, "LensPosition": (1/distance)})
    print('there')
    picam2.start_recording(JpegEncoder(), FileOutput(output), Quality.VERY_HIGH)
    metadata = picam2.capture_metadata()
    print(metadata["AnalogueGain"])
    print(metadata["ColourGains"])
    #out = StreamingOutput()
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        picam2.stop_recording()
