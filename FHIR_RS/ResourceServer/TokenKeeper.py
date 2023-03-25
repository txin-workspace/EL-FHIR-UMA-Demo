import KeycloakAccess
from time import sleep
import threading
from datetime import datetime
import Log

# logging.basicConfig(level=logging.DEBUG)

client_token = None
token_acitve_flag = False
token_expires = 0

def start_keeper():
    threading.Thread(target=job).start()

def job():
    while True:
        try:
            refrech_client_token()
        except Exception as exc:
            Log.error('[refrech_client_token] {}'.format(exc))
            sleep(5)
            continue
        sleep(295)


def refrech_client_token():
    global token_acitve_flag
    global client_token
    global token_expires

    token_acitve_flag = False

    while True:
        Log.info('[refrech_client_token] {}'.format(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")))
        result, token = KeycloakAccess.get_client_token()

        if result == False:
            Log.error('[refrech_client_token] FIELD!!')
            sleep(0.3)
            continue

        else:
            Log.info('[refrech_client_token] successed')
            client_token = token
            token_acitve_flag = True
            token_expires = 300

            break