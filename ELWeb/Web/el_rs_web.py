from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import abort
from flask import json
from flask_cors import CORS
import web_config
import sys
import Log
import ElRsAccess
from time import sleep



app = Flask(__name__)
CORS(app)



@app.route('/callback/test', methods=['GET'], strict_slashes=False)
def test():
    return {
        'args': str(request.args),
        'form': str(request.form),
        'headers': str(request.headers),
        'data': str(request.data)
    }, 200



@app.route('/index', methods=['GET'], strict_slashes=False)
def index():
    return render_template(
        'index.html',
        el_am_host = web_config.el_am_host,
        el_am_port = web_config.el_am_port,
        el_am_realm = web_config.el_am_realm_name,
        client_id = web_config.client_id,
        client_redirect_url = web_config.client_redirect_url,
    )



@app.route('/ready', methods=['GET'], strict_slashes=False)
def server_ready():
    return 200



@app.route('/devices', methods=['GET'], strict_slashes=False)
def get_patient():

    if 'Access-Token' not in request.headers:
        abort(400)

    result, patient_list = ElRsAccess.get_dev_info(request.headers['Access-Token'])
    if result != True:
        abort(400)

    return {'devices': patient_list}



@app.route('/share', methods=['POST'], strict_slashes=False)
def res_share():
    if 'Access-Token' not in request.headers:
        abort(400)

    # if 'res_type' not in request.get_json() or 'res_id' not in request.get_json() or 'target_user' not in request.get_json():
    #     abort(400)

    result = ElRsAccess.share_res(
        request.get_json()['res_id'], request.headers['Access-Token'], request.get_json()['target_user'])

    if result != True:
        return 'field', 200

    return 'success', 200



@app.route('/unshare', methods=['DELETE'], strict_slashes=False)
def res_unshare():
    if 'Access-Token' not in request.headers:
        abort(400)

    # if 'res_type' not in request.get_json() or 'res_id' not in request.get_json() or 'policy_id' not in request.get_json():
    #     abort(400)

    # Log.error('{}'.format(request.get_json()))

    result = ElRsAccess.unshare_res(
        request.get_json()['res_id'], request.headers['Access-Token'], request.get_json()['policy_id']
    )

    if result != True:
        return 'field', 200

    return 'success', 200



@app.route('/', methods=['GET'], strict_slashes=False)
def sso_test():

    return redirect('https://{}:{}/realms/{}/protocol/openid-connect/auth?response_type=token&client_id={}&redirect_uri={}&flow=implicit&useNonce=true'.format(
        web_config.el_am_host,
        web_config.el_am_port,
        web_config.el_am_realm_name,
        web_config.client_id,
        web_config.client_redirect_url
        ))



def init(el_rs_host, el_rs_port, 
el_am_host, el_am_port, el_am_realm_name, 
client_id, client_redirect_url):

    web_config.el_rs_host = el_rs_host
    web_config.el_rs_port = el_rs_port

    web_config.el_am_host = el_am_host
    web_config.el_am_port = el_am_port
    web_config.el_am_realm_name = el_am_realm_name

    web_config.client_id = client_id
    web_config.client_redirect_url = client_redirect_url



def server_args_check(list_args):
    Log.debug('{}'.format(list_args))
    if len(list_args) != 8:
        return False
    # if '.' not in list_args[5]:
    #     return False
    return True



def depend_server_check():
    while True:
        if ElRsAccess.check_rs_ready() != True:
            Log.info('EL RS not ready')
            sleep(10)
            continue

        break

   

def main(list_args):

    Log.info('[check server initialization parameters]')
    if not server_args_check(list_args):
        Log.info('usage:\n\tel_rs_host el_rs_port el_am_host el_am_port health_am_real_name client_id client_redirect_url')
        return

    Log.info('[initialization demo app server config]')
    init(list_args[1], list_args[2], list_args[3], list_args[4], list_args[5], list_args[6], list_args[7])

    Log.info('parameters: \
        \n\tel_rs_host: {} \n\tel_rs_port: {}\
        \n\tel_am_host: {} \n\tel_am_port: {} \n\tel_am_realm_name: {}\
        \n\tclient_id: {} \n\tclient_redirect_url: {}'.format(
            web_config.el_rs_host, web_config.el_rs_port, 
            web_config.el_am_host, web_config.el_am_port, web_config.el_am_realm_name, 
            web_config.client_id, web_config.client_redirect_url))

    Log.info('[check depend server ready]')
    depend_server_check()

    Log.info('[start ECHOENT Lite Web server]')
    app.run(host='0.0.0.0', port='13000', debug=False)



if __name__ == '__main__':
    main(sys.argv)
