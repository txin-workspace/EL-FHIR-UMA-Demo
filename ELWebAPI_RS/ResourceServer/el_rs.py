from flask import Flask
# from flask import request
# from flask import Response
# from flask import abort
from flask_cors import CORS
import sys
from DeviceApi import device_api
from HealthApi import health_api
from PermissionApi import permission_api
from time import sleep
from TokenKeeper import start_keeper
from RsPollingAgent import start_agent
from KeycloakAccess import check_am_ready_uma
from HealthRsAccess import check_rs_ready

import rs_config
import Log


app = Flask(__name__)
app.register_blueprint(device_api, url_prefix = '/elapi/v1/devices')
app.register_blueprint(health_api, url_prefix = '/elapi/v1/healthCareRecords')
app.register_blueprint(permission_api, url_prefix = '/elapi')

CORS(app)



@app.route('/', methods=['GET'], strict_slashes=False)
def server_ready():
    return '', 200



def init(am_host, am_port, real_name, 
client_id, client_scret, web_client_id, 
health_rs_host, health_rs_port, 
agent_name_health, agent_pw_health,
agent_name_el, agent_pw_el):

    rs_config.am_host = am_host
    rs_config.am_port = am_port
    rs_config.realm_name = real_name

    rs_config.client_id = client_id
    rs_config.client_screct = client_scret
    rs_config.web_client_id = web_client_id

    rs_config.health_rs_host = health_rs_host
    rs_config.health_rs_port = health_rs_port

    rs_config.agent_name_health = agent_name_health
    rs_config.agent_pw_health = agent_pw_health

    rs_config.agent_name_el = agent_name_el
    rs_config.agent_pw_el = agent_pw_el



def server_args_check(list_args):
    Log.debug('{}'.format(list_args))
    if len(list_args) != 13:
        return False
    # if '.' not in list_args[1] or '.' not in list_args[7]:
    #     return False
    return True


def depend_server_check():
    while True:
        if check_am_ready_uma() != True:
            Log.info('\tAM not ready')
            sleep(10)
            continue
        if check_rs_ready() != True:
            Log.info('\tHealth RS not ready')
            sleep(10)
            continue

        break


def main(list_args):

    Log.info('[check server initialization parameters]')
    if not server_args_check(list_args):
        Log.info('usage:\n\tam_host am_port real_name client_id client_scret \
            web_client_id health_rs_host health_rs_port \
                agent_name_health agnet_pw_health agent_name_el agnet_pw_el')
        return

    Log.info('[initialization ECHONET Lite Resource server config]')
    init(list_args[1], list_args[2], list_args[3], list_args[4], 
        list_args[5], list_args[6], list_args[7], list_args[8], 
        list_args[9], list_args[10], list_args[11], list_args[12])

    Log.info('parameters: \
        \n\tam_host: {} \n\tam_port: {} \n\treal_name: {} \
        \n\tclient_id: {} \n\tclient_scret: {} \n\tweb_client_id: {} \
        \n\thealth_rs_host: {} \n\thealth_rs_port: {} \
        \n\tagent_name_health: {} \n\tel_agent_pw_health: {} \
        \n\tagent_name_el: {} \n\tel_agent_pw_el: {}'.format(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name, 
        rs_config.client_id, rs_config.client_screct, rs_config.web_client_id, 
        rs_config.health_rs_host, rs_config.health_rs_port, 
        rs_config.agent_name_health, rs_config.agent_pw_health,
        rs_config.agent_name_el, rs_config.agent_pw_el
    ))

    Log.info('[check depend server ready]')
    depend_server_check()

    Log.info('[start Resource server client token keeper]')
    start_keeper()

    Log.info('[start Health Resource server polling agent]')
    start_agent()

    Log.info('[start EL Resource server]')
    app.run(host='0.0.0.0', port='10000', debug=False)


if __name__ == '__main__':
    main(sys.argv)
