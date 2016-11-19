import requests
from flask import Flask, render_template, Response
import cv2
import datetime

from flask import Flask, redirect
from pyfcm import FCMNotification

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notify')
def notify():
    return render_template('notify.html')

def gen(Camera):
    while True:
        frame = Camera.detectmove()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(MoveDetector(1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


class MoveDetector:
    def __init__(self):
        self.detectmove()

    def frameDiff(self, t0, t1, t2):

        dI1 = cv2.absdiff(t2, t1)
        dI2 = cv2.absdiff(t1, t0)

        return cv2.bitwise_and(dI1, dI2)
    def detectmove(self):
        capture = cv2.VideoCapture(0)

        winName = "Motion Detector"
        cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)



        frameBefore = cv2.cvtColor(capture.read()[1], cv2.COLOR_RGB2GRAY)
        framePresent = cv2.cvtColor(capture.read()[1], cv2.COLOR_RGB2GRAY)
        frameNext = cv2.cvtColor(capture.read()[1], cv2.COLOR_RGB2GRAY)

        last_time = datetime.datetime.now()
        actual_time = datetime.datetime.now()

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
                time_delta = actual_time.second - last_time.second
                actual_time = datetime.datetime.now()
                #print actual_time, "     " , last_time
                if cv2.contourArea(contour) < 200:
                    continue

                if cv2.contourArea(contour) > 200 and time_delta > 15:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print "wykryto ruch"
                    last_time = actual_time

                    headers = {"Content-Type": "application/json",
                            "Authorization": "key=AIzaSyDHdW5TlcGBwReOe5WhRBoH3aDzRlVmbNU"}

                    json = '{"notification": {"body" : "Move was detected!","title" : "Check it!"},"to":"/topics/movementDetection",}'

                    r = requests.post('https://fcm.googleapis.com/fcm/send', data=json, headers=headers)
                    # Notification('title', 'mojamessage')

            cv2.imshow( winName, frame )
            ret, jpeg = cv2.imencode('.jpeg', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                 break

            #return jpeg.tobytes()
        capture.release()
        cv2.destroyWindow(winName)



# class Notification:
#     def __init__(self,title, message):
#         self.title = title
#         self.message = message
#         self.API_Key = 'key=AIzaSyDHdW5TlcGBwReOe5WhRBoH3aDzRlVmbNU'
#         self.url = 'https://fcm.googleapis.com/fcm/send'
#         self.push_notofication()
#
#     def push_notofication(self):
#         header = {"Content-Type": "application/json",
#                 "Authorization": self.API_Key}
#         json = {"notification": {"body" : self.message,
#                "title" : self.title},"to":"/topics/movementDetection",}
#         requests.post('https://fcm.googleapis.com/fcm/send', json=json, headers=header)






if __name__ == '__main__':
    print cv2.__version__
    #app.run(host='127.0.0.1', debug=True)
    MoveDetector()