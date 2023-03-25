from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import abort
from flask_cors import CORS
import app_config
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
        el_am_host = app_config.el_am_host,
        el_am_port = app_config.el_am_port,
        el_am_realm = app_config.el_am_realm_name,
        client_id = app_config.client_id,
        client_redirect_url = app_config.client_redirect_url,
    )

@app.route('/beforeindex', methods=['GET'], strict_slashes=False)
def beforeindex():
    return render_template(
        'beforeindex.html',
        app_am_host = app_config.app_am_host,
        app_am_port = app_config.app_am_port,
        app_am_realm = app_config.app_am_realm,
        app_client_id = app_config.app_client_id,
        app_client_redirect_url = app_config.app_client_redirect_url,
        el_am_host = app_config.el_am_host,
        el_am_port = app_config.el_am_port,
        el_am_realm = app_config.el_am_realm_name,
        client_id = app_config.client_id,
        client_redirect_url = app_config.client_redirect_url,
    )


@app.route('/ready', methods=['GET'], strict_slashes=False)
def server_ready():
    return 200



@app.route('/device', methods=['GET'], strict_slashes=False)
def get_dev():

    if 'Access-Token' not in request.headers:
        abort(400)

    return {'devices': ElRsAccess.get_el_dev(request.headers['Access-Token'])}



@app.route('/health', methods=['GET'], strict_slashes=False)
def get_health():
    if 'Access-Token' not in request.headers:
        abort(400)

    return {'health': ElRsAccess.get_el_health(request.headers['Access-Token'])}



# @app.route('/', methods=['GET'], strict_slashes=False)
# def sso_test():

#     return redirect('https://{}:{}/realms/{}/protocol/openid-connect/auth?response_type=token&client_id={}&redirect_uri={}&flow=implicit&useNonce=true'.format(
#         # '150.65.173.141',
#         app_config.el_am_host,
#         # '8081',
#         app_config.el_am_port,
#         # 'ELWebAPI-m',
#         app_config.el_am_realm_name,
#         # 'health_care_app',
#         app_config.client_id,
#         # 'http://150.65.173.141:11000/index'
#         app_config.client_redirect_url
#         ))
@app.route('/', methods=['GET'], strict_slashes=False)
def sso_test():

    return redirect('https://{}:{}/realms/{}/protocol/openid-connect/auth?response_type=token&client_id={}&redirect_uri={}&flow=implicit&useNonce=true'.format(
        app_config.app_am_host,
        app_config.app_am_port,
        app_config.app_am_realm,
        app_config.app_client_id,
        app_config.app_client_redirect_url
        ))



def init(rs_host, rs_port, 
el_am_host, el_am_port, el_am_realm_name, 
client_id, client_redirect_url,
app_am_host, app_am_port, app_am_realm_name, 
app_client_id, app_client_redirect_url):

    app_config.rs_host = rs_host
    app_config.rs_port = rs_port

    app_config.el_am_host = el_am_host
    app_config.el_am_port = el_am_port
    app_config.el_am_realm_name = el_am_realm_name

    app_config.client_id = client_id
    app_config.client_redirect_url = client_redirect_url


    app_config.app_am_host = app_am_host
    app_config.app_am_port = app_am_port
    app_config.app_am_realm = app_am_realm_name

    app_config.app_client_id = app_client_id
    app_config.app_client_redirect_url = app_client_redirect_url



def server_args_check(list_args):
    Log.debug('{}'.format(list_args))
    if len(list_args) != 13:
        return False
    # if '.' not in list_args[5]:
    #     return False
    return True



def depend_server_check():
    while True:
        if ElRsAccess.check_rs_ready() != True:
            Log.info('\tHealth RS not ready')
            sleep(10)
            continue

        break

   

def main(list_args):

    Log.info('[check server initialization parameters]')
    if not server_args_check(list_args):
        Log.info('usage:\n\tel_rs_host el_rs_port el_am_host el_am_port el_am_real_name client_id client_redirect_url app_am_host app_am_port app_am_real_name app_client_id app_client_redirect_url')
        return

    Log.info('[initialization demo app server config]')
    init(list_args[1], list_args[2], list_args[3], list_args[4], list_args[5], list_args[6], list_args[7],
        list_args[8], list_args[9], list_args[10], list_args[11], list_args[12])

    Log.info('parameters: \
        \n\trs_host: {} \n\trs_port: {}\
        \n\tel_am_host: {} \n\tel_am_port: {} \n\tel_am_realm_name: {}\
        \n\tclient_id: {} \n\tclient_redirect_url: {}\
        \n\tapp_am_host: {} \n\tapp_am_port: {} \n\tapp_am_realm_name: {}\
        \n\tapp_client_id: {} \n\tapp_client_redirect_url: {}'.format(
            app_config.rs_host, app_config.rs_port, 
            app_config.el_am_host, app_config.el_am_port, app_config.el_am_realm_name, 
            app_config.client_id, app_config.client_redirect_url,
            app_config.app_am_host, app_config.app_am_port, app_config.app_am_realm, 
            app_config.app_client_id, app_config.app_client_redirect_url))

    Log.info('[check depend server ready]')
    depend_server_check()

    Log.info('[start health care application demo server]')
    app.run(host='0.0.0.0', port='11000', debug=False)



if __name__ == '__main__':
    main(sys.argv)
