import KeycloakAccess
import HealthRsAccess
from time import sleep
import threading
from datetime import datetime
import Log
import rs_config

client_token = None
client_token_acitve_flag = False
client_token_expires = 0


health_rs_agent_token = None
health_rs_agent_token_acitve_flag = False
health_rs_agent_token_expires = 0


agent_token = None
agent_token_acitve_flag = False
agent_token_expires = 0



def start_keeper():
    threading.Thread(target=job_client_token).start()
    threading.Thread(target=job_agent_token_health).start()
    threading.Thread(target=job_agent_token_el).start()


def job_client_token():
    while True:
        try:
            refrech_client_token()
        except Exception as exc:
            Log.error('[refrech_client_token] {}'.format(exc))
            sleep(5)
            continue

        sleep(295)



def job_agent_token_health():
    while True:
        try:
            refrech_health_rs_agent_token()
        except Exception as exc:
            Log.error('[refrech_agent_token_health] {}'.format(exc))
            sleep(5)
            continue

        sleep(295)


def job_agent_token_el():
    while True:
        try:
            refrech_agent_token()
        except Exception as exc:
            Log.error('[refrech_agent_token_el] {}'.format(exc))
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
            Log.error('[refrech_client_token] FAILED!!')
            sleep(0.3)
            continue

        else:
            Log.info('[refrech_client_token] successed')
            client_token = token
            token_acitve_flag = True
            token_expires = 300

            break    



def refrech_health_rs_agent_token():
    global health_rs_agent_token
    global health_rs_agent_token_expires
    global health_rs_agent_token_acitve_flag

    health_rs_agent_token_acitve_flag = False

    while True:
        Log.info('[refrech_health_rs_agent_token] {}'.format(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")))
        result, token, expires = HealthRsAccess.get_user_token(
            rs_config.agent_name_health, rs_config.agent_pw_health
        )

        if result == False:
            Log.error('[refrech_health_rs_agent_token] FAILED!!')
            sleep(0.3)
            continue

        else:
            Log.info('[refrech_health_rs_agent_token] successed')
            health_rs_agent_token = token
            health_rs_agent_token_acitve_flag = True
            health_rs_agent_token_expires = 300

            break    

def refrech_agent_token():
    global agent_token
    global agent_token_expires
    global agent_token_acitve_flag

    agent_token_acitve_flag = False

    while True:
        Log.info('[refrech_agent_token] {}'.format(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")))
        resp = KeycloakAccess.get_user_token(
            rs_config.agent_name_el, rs_config.agent_pw_el
        )

        if resp.status_code != 200:
            Log.error('[refrech_agent_token] FAILED!!')
            sleep(0.3)
            continue

        else:
            Log.info('[refrech_agent_token] successed')
            agent_token = resp.json()['access_token']
            agent_token_acitve_flag = True
            agent_token_expires = 300

            break    
