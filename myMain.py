import argparse
from Notification import Notification
import NEW



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--reg-id', dest='registration_id', required=True)
    parser.add_argument('-m', '--message', dest='message', required=True)
    args = parser.parse_args()
    Notification.send_push_notification(args.registration_id, args.message)