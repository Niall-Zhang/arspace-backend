import requests
from arspace import settings
from utils.constants import ERROR, FALSE, FIREBASE_NOTIFICATION_FAILED, FIREBASE_NOTIFICATION_SUCCESS, MESSAGE, SUCCESS, TRUE
import logging
logger = logging.getLogger(__name__)

# Send fcm notification to single recipient
def send_notification_using_fcm(payload):
    try:
        data = {
            'notification': {
                'title': payload['title'],
                'body': payload['body']
            },
            "priority":"high",
            'data': {},
            "to":payload['device_token']
        }
        logger.info(f"method:send_notification_using_fcm, data: {data}")
        # Send the notification
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            json=data,
            headers={
                'Authorization': f"key={settings.FIREBASE_SERVER_KEY}",                
                'Content-Type': 'application/json'
            }
        )
         
        logger.info(f"method:send_notification_using_fcm, response: {response.json()}")
        # Check the response status
        if response.status_code == 200:
            return {SUCCESS:TRUE,MESSAGE:FIREBASE_NOTIFICATION_SUCCESS}
        else:
            return {SUCCESS:FALSE,ERROR:FIREBASE_NOTIFICATION_FAILED}
    except Exception as ex:
        logger.error(f"method:send_notification_using_fcm, error:{str(ex)}")
        return {SUCCESS:FALSE,ERROR:str(ex)}
    

# Send fcm notification to multiple recipients
def send_notifications_using_fcm(payload):
    try: 
        device_tokens = payload['device_token']
        print(f"device_tokens >>>>>>>>>>>>>>>>>>>>>> {device_tokens}")
        data = {
            'registration_ids': device_tokens,
            "priority":"high",
            'notification': {
                'title': payload['title'],
                'body': payload['body'],
            }
        }
        logger.info(f"method:send_notifications_using_fcm, data: {data}")
        # Send the notification
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            json=data,
            headers={
                'Authorization': f"key={settings.FIREBASE_SERVER_KEY}",                
                'Content-Type': 'application/json'
            }
        )
         
        logger.info(f"method:send_notifications_using_fcm, response: {response.json()}")
        # Check the response status
        if response.status_code == 200:
            return {SUCCESS:TRUE,MESSAGE:FIREBASE_NOTIFICATION_SUCCESS}
        else:
            return {SUCCESS:FALSE,ERROR:FIREBASE_NOTIFICATION_FAILED}
    except Exception as ex:
        logger.error(f"method:send_notification_using_fcm, error:{str(ex)}")
        return {SUCCESS:FALSE,ERROR:str(ex)}