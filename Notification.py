from gcm import GCM

class Notification:
    def __init__(self, API_Key):
        self.API_Key = API_Key


    def send_push_notification(self, registration_id, message):
        gcm = GCM(self.API_Key)
        resp = gcm.plaintext_request(registration_id=registration_id,
                                     data={'message': message})