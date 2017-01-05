import requests
from flask import Flask, render_template, Response
import cv2
import datetime
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import HttpHandler

class Notification:
    def __init__(self, title, message):
        self.title = title
        self.message = message
        self.API_Key = 'key=AIzaSyDHdW5TlcGBwReOe5WhRBoH3aDzRlVmbNU'
        self.url = 'https://fcm.googleapis.com/fcm/send'

    def push(self):
        header = {"Content-Type": "application/json",
                "Authorization": self.API_Key}
        json = {"notification": {"body" : self.message,
               "title" : self.title},"to":"/topics/movementDetection",}
        requests.post('https://fcm.googleapis.com/fcm/send', json=json, headers=header)


class MoveDetector:
    def __init__(self):
        self.last_time = datetime.datetime(1970, 1, 1)
        self.event = threading.Event()
        self.lock = threading.Lock()

    def getFrame(self):
        self.event.wait()
        # self.lock.acquire()
        return self.frame

    def releaseFrame(self):
        # self.lock.release()
        pass

    def frameDiff(self, t0, t1, t2):

        dI1 = cv2.absdiff(t2, t1)
        dI2 = cv2.absdiff(t1, t0)

        return cv2.bitwise_and(dI1, dI2)
    def detectmove(self):
        capture = cv2.VideoCapture(0)
        capture.set(3, 320)
        capture.set(4, 240)

        frameBefore = cv2.cvtColor(capture.read()[1], cv2.COLOR_RGB2GRAY)
        framePresent = cv2.cvtColor(capture.read()[1], cv2.COLOR_RGB2GRAY)
        frameNext = cv2.cvtColor(capture.read()[1], cv2.COLOR_RGB2GRAY)

        notification = Notification("Check it!", "Movement was detected")

        while True:

            frameBefore = framePresent
            framePresent = frameNext
            frame = capture.read()[1]
            frameNext = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            myThreshold = cv2.threshold(self.frameDiff(frameBefore, framePresent, frameNext), 25, 255, cv2.THRESH_BINARY)[1]

            myThreshold = cv2.dilate(myThreshold, None, iterations=2)

            (contours, _) = cv2.findContours(myThreshold.copy(), cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) > 150:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print "wykryto ruch"

                    current_time = datetime.datetime.utcnow()
                    time_delta = current_time - self.last_time
                    if time_delta.total_seconds() >= 60:
                        self.last_time = current_time
                        print "wysylam notyfikacje"
                        notification.push()

            #cv2.imshow( winName, frame )
            ret, jpeg = cv2.imencode('.jpeg', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            self.event.clear()
            self.frame = jpeg.tobytes()
            self.event.set()
            return self.frame
        capture.release()
        #cv2.destroyWindow(winName)

detector = MoveDetector()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(detector):
    while True:

        frame = detector.getFrame()
        yield (b'--frame\r\n'
               b'Content-Length: ' + str(len(frame)) + b'\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        detector.releaseFrame()

@app.route('/video')
def video():
    return Response(gen(detector),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def motionDetectionThread(detector):
    while True:
        frame = detector.detectmove()

if __name__ == '__main__':
    print cv2.__version__

    thread = threading.Thread(target=motionDetectionThread, kwargs={ 'detector': detector })
    thread.start()

    #app.run(host='127.0.0.1', debug=True)
    app.run(host='192.168.1.165', threaded=True, debug=False)

