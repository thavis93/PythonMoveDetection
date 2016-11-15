import cv2
import datetime
from pyfcm import FCMNotification



class MoveDetector:
    def __init__(self, API_Key):
        self.API_Key = API_Key
        self.detectmove()

    def frameDiff(self, t0, t1, t2):

        dI1 = cv2.absdiff(t2, t1)
        dI2 = cv2.absdiff(t1, t0)

        return cv2.bitwise_and(dI1, dI2)
    def detectmove(self):
        #capture = cv2.VideoCapture(0)
        capture = cv2.VideoCapture("udp://127.0.0.1:5000/")

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

            (cnts, _) = cv2.findContours(myThreshold.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

            for c in cnts:
                time_delta = actual_time.second - last_time.second
                actual_time = datetime.datetime.now()
                #print actual_time, "     " , last_time
                if cv2.contourArea(c) < 100:
                    continue

                if cv2.contourArea(c) > 100 and time_delta > 5:
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print "wykryto ruch"
                    last_time = actual_time
                    #TODO: tutaj notifikacja jak cos


            cv2.imshow( winName, frame )
            #ret, jpeg = cv2.imencode('.jpeg', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                 break
            #return jpeg.tobytes()
        capture.release()
        cv2.destroyWindow(winName)

MoveDetector(1)

class Notification:
    def __init__(self):
        Notification()

    API_Key = "AIzaSyDHdW5TlcGBwReOe5WhRBoH3aDzRlVmbNU"
    push_service = FCMNotification(api_key=API_Key)

    registration_id = "1:222781398709:android:a799a9148afbd3c9"

    message_title = "moja wiadomosc"
    message_body = "srodek wiadomosci"

    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

    print result



