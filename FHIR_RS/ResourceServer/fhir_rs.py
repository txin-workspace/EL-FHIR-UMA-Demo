from flask import Flask
from flask_cors import CORS
from flask import request
from flask import Response
from flask import abort
from flask import json
import sys
import rs_config
import KeycloakAccess
import HapiAccess
from TokenKeeper import start_keeper
from time import sleep

import urllib3
from urllib3.exceptions import InsecureRequestWarning
import Log

# import logging

# logging.basicConfig(
#     level=logging.DEBUG, 
#     format='%(asctime)s\t%(levelname)s\n%(message)s')

urllib3.disable_warnings(InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# {res_id: HR}
res_dict = {}

class HealthResource():
    def __init__(self) -> None:
        self.res_id = None
        self.res_type = None
        self.shared = []

        self.hapi_res_id = None
        self.hapi_res_type = None
        self.hapi_patient_id = None

        self.proxy_share = {}

    def getInfo(self):
        return {
            'patient': self.hapi_patient_id,
            'hapi_type': self.hapi_res_type,
            'hapi_id': self.hapi_res_id,
            'shared_with': self.shared,
            'resource_id': self.res_id,
            'resource_type': self.res_type,
            'proxy_share': self.proxy_share
        }

    def getInfo_share(self):
        return {
            'patient': self.hapi_patient_id,
            'hapi_type': self.hapi_res_type,
            'hapi_id': self.hapi_res_id,
            # 'shared_with': self.shared,
            'resource_id': self.res_id,
            'resource_type': self.res_type,
            'proxy_share': self.proxy_share
        }

@app.route('/', methods=['GET'], strict_slashes=False)
def server_ready():
    return '', 200

@app.route('/login', methods=['POST'], strict_slashes=False)
def hapi_rs_login():
    # user_id = ''
    # user_password = ''

    try :
        user_id = request.get_json()['user_id']
    except:
        Log.error("[login] no user_id")
        abort(400)

    try :
        user_password = request.get_json()['user_password']
    except:
        Log.error("[login] no user_password")
        abort(400)

    resp = KeycloakAccess.get_user_token(user_id, user_password)
    
    return resp.json(), resp.status_code

@app.route('/fhir/<hapi_res_type>', methods=['GET'], strict_slashes=False)
def hapi_get_list(hapi_res_type):
    
    # check user ideneity
    if 'Access-Token' not in request.headers:
        abort(401)

    result, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])
    if result == False:
        abort(401)

    # check user owned resource
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result == False:
        abort(401)

    return_list = []

    # find all respurces, check type , dump info
    global res_dict
    for res_id in list_own_resid:
        
        if res_id not in res_dict:
            continue

        if res_dict[res_id].hapi_res_type != hapi_res_type:
            continue

        #　TODO 
        return_list.append(res_dict[res_id].getInfo())
        # TODO

    return Response(json.dumps(return_list), mimetype='application/json')



@app.route('/fhir/<hapi_res_type>', methods=['POST'], strict_slashes=False)
def hapi_create(hapi_res_type):

    # check user idenenty
    if 'Access-Token' not in request.headers:
        abort(401)

    result, uid, client = KeycloakAccess.token_get_uid(
        request.headers['Access-Token'])
    if result != True:
        abort(401)

    res_content = None
    patient_id = None

    # check res type and add users idenenty to resource content
    # if patient, add am user id in 'identifier'
    if hapi_res_type == "Patient":
        # 
        # TODO
        # maybe need to check this uid is already have a patient
        # when this uid created a patinet, secand times create need to be block?
        # 
        res_content = request.get_json()
        res_content['identifier'] = {
            "type": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/v2/0203",
                        "code": "AN"
                    }
                ]
            },
            "value": uid
        }
    # if observation, search patient using am identifier, add patient id in 'subject' 'reference'
    elif hapi_res_type == "Observation":
        # get hapi patient id
        result, patient_id_list = HapiAccess.search_patient_id(
            dict(request.headers), uid)
        if result != True:
            abort(500)

        res_content = request.get_json()
        if 'subject' in res_content:
            if 'reference' in res_content['subject']:
                if res_content['subject']['reference'].replace('Patient/', '') not in patient_id_list:
                    abort(401)
                else:
                    patient_id = res_content['subject']['reference'].replace('Patient/', '')
        # res_content['subject']['reference'] = 'Patient/{}'.format(patient_id)

        
    # create resource in hapi sercer
    result, res_hapi_res_type, res_hapi_res_id, resp = HapiAccess.create_resource(
        hapi_res_type, dict(request.headers), res_content
    )
    if result != True:
        abort(500)

    # register resource to keycloak
    result, am_res_id = KeycloakAccess.create_resource(
        '{}-{}'.format(res_hapi_res_type, res_hapi_res_id), uid)
    if result != True:
        abort(500)

    # save to local dict
    global res_dict
    res_dict[am_res_id] = HealthResource()
    res_dict[am_res_id].res_id = am_res_id
    res_dict[am_res_id].res_type = get_res_type_from_content(
        hapi_res_type, res_content)
    res_dict[am_res_id].hapi_res_id = res_hapi_res_id
    res_dict[am_res_id].hapi_res_type = res_hapi_res_type
    if res_hapi_res_type == "Patient":
        res_dict[am_res_id].hapi_patient_id = res_hapi_res_id
    else:
        res_dict[am_res_id].hapi_patient_id = patient_id
    

    return resp.json(), resp.status_code

def get_res_type_from_content(hapi_res_type, res_content) -> list:
    if hapi_res_type == 'Patient':
        del res_content['resourceType']
        del res_content['identifier']
        return_list = list(res_content.keys())
        return_list.append('id')
        return return_list

    elif hapi_res_type == 'Observation':
        type_list = []
        if 'component' in res_content:
            for comp in res_content['component']:
                type_list.append(
                    loinc_code_conver(comp['code']['coding'][0]['code']))
        else:
            type_list.append(
                    loinc_code_conver(res_content['code']['coding'][0]['code']))

        # if 'bloodPressure-s' in type_list and 'bloodPressure-d' in type_list:
        #     type_list.remove('bloodPressure-s')
        #     type_list.remove('bloodPressure-d')
        #     type_list.append('bloodPressure')

        return type_list

    else:
        Log.warning('[get_res_type_from_content] other: {}'.format(hapi_res_type))
        return []

def loinc_code_conver(code):
    Log.debug('[loinc_code_conver] {}'.format(code))
    if code == '8310-5':
        return 'bodyTemperature'

    elif code == '29463-7':
        return 'bodyWeight'

    elif code == '39156-5':
        return 'bmi'

    elif code == '8480-6':
        return 'bloodPressure-s'

    elif code == '8462-4':
        return 'bloodPressure-d'

    elif code == '8867-4':
        return 'heartRate'
    
    elif code == '59408-5':
        return 'pulseOximetry'

    else:
        Log.warning('[loinc_code_conver] other: {}'.format(code))
        return ''

@app.route('/fhir/<hapi_res_type>/<hapi_res_id>', methods=['GET'], strict_slashes=False)
def hapi_read(hapi_res_type, hapi_res_id):

    result, res_id = find_res_by_type_id(hapi_res_type, hapi_res_id)
    if result != True:
        abort(404)
    
    # request ticket
    if 'Access-Token' not in request.headers and 'RPT' not in request.headers:
        # no token, rerturn ticket
        return retuen_permisson_ticket(res_id)

    # access as owner
    elif 'Access-Token' in request.headers and 'RPT' not in request.headers:
        # check user identity
        result, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])
        if result != True:
            abort(401)

        # get user owned resource
        result, list_own_resid = KeycloakAccess.check_own_resource(uid)
        if result != True:
            abort(401)

        # find target resource and check permission
        if res_id not in list_own_resid:
            abort(401)

        result, resp = HapiAccess.get_resource(
            hapi_res_type, hapi_res_id, dict(request.headers))

        return resp.json(), resp.status_code

    # requesting party
    elif 'Access-Token' not in request.headers and 'RPT' in request.headers:
        pass
        # check rpt
        result, rpt_detail = KeycloakAccess.check_rpt(request.headers['RPT'])
        if result != True:
            # check not pass, return ticket
            return retuen_permisson_ticket(res_id)

        # check permission, and permissnion resource id
        for p in rpt_detail['permissions']:
            if 'data_read' not in p['scopes']:
                continue
            if p['resource_id'] != res_id:
                continue

        # if all pass , get and return resource, whatever result success or not
        resp = HapiAccess.get_resource(
            hapi_res_type, hapi_res_id, dict(request.headers))
        
        return resp.json(), resp.status_code
    
    # access token and rpt in headers, return 401
    else:
        abort(401)


@app.route('/fhir/<hapi_res_type>/<hapi_res_id>', methods=['DELETE'], strict_slashes=False)
def hapi_delete(hapi_res_type, hapi_res_id):

     # check user identity
    if 'Access-Token' not in request.headers:
        abort(401)

    result, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])
    if result != True:
        abort(401)

    # check user owned resource
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        abort(401)

    # find resource  and check type and id, delete resource
    global res_dict
    for res_id in res_dict:
        if res_dict[res_id].hapi_res_type != hapi_res_type:
            continue

        if res_dict[res_id].hapi_res_id != hapi_res_id:
            continue

        if res_id not in list_own_resid:
            abort(401)
        
        # delete in am
        result = KeycloakAccess.delete_resource(res_id)
        if result != True:
            abort(500)

        # delete in hapi
        result, resp =  HapiAccess.delete_resource(
            hapi_res_type, hapi_res_id, dict(request.headers))

        if result != True:
            abort(500)

        # delete in local
        del res_dict[res_id]

        # return original hapi response
        return resp.json(), resp.status_code

    abort(404)

# @app.route('/<hapi_res_type>/<hapi_res_id>', methods=['PUT'], strict_slashes=False)
# def hapi_update(hapi_res_type, hapi_res_id):
#     pass



@app.route('/share/<hapi_res_type>/<hapi_res_id>', methods=['GET'], strict_slashes=False)
def hapi_check_shared(hapi_res_type, hapi_res_id):

    # check user identity
    if 'Access-Token' not in request.headers:
        abort(401)

     # check identity 
    result, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])
    if result != True:
        abort(401)

    # check resource exist or not
    result, res_id = find_res_by_type_id(hapi_res_type, hapi_res_id)
    if result != True:
        Log.error('not found resource {} {}'.format(hapi_res_type, hapi_res_id))
        abort(404)

    # check user owned resource
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        abort(401)
    
    if res_id not in list_own_resid:
        abort(401)

    result, list_policy = KeycloakAccess.check_resource_shared(
        request.headers['Access-Token'], res_id)
    if result != True:
        abort(500)

    # return {'shared': list_policy}
    return Response(json.dumps(list_policy), mimetype='application/json')



@app.route('/share/<hapi_res_type>/<hapi_res_id>', methods=['POST'], strict_slashes=False)
def hapi_create_share(hapi_res_type, hapi_res_id):

    # check user identity
    if 'Access-Token' not in request.headers:
        abort(401)

     # check identity 
    result, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])
    if result != True:
        abort(401)

    # check resource exist or not
    result, res_id = find_res_by_type_id(hapi_res_type, hapi_res_id)
    if result != True:
        Log.error('not found resource {} {}'.format(hapi_res_type, hapi_res_id))
        abort(404)

    # check user owned resource
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        abort(401)
    
    if res_id not in list_own_resid:
        abort(401)

    # request body:
    # {"target": "rs-elwbeapi:xxxxxxxx", "target_type": "service / user"}
    if request.get_json()['target'][:12] == "rs-elwebapi:":
        result, policy_id = KeycloakAccess.share_resource_hapi(
            request.headers['Access-Token'], res_id,
            request.get_json()['target_type'], 
            request.get_json()['target'][12:]
        )
    else:
        result, policy_id = KeycloakAccess.share_resource(
            request.headers['Access-Token'], res_id,
            request.get_json()['target_type'], 
            request.get_json()['target']
        )
    if result != True:
        Log.error('[create policy] FIELD!!!')
        abort(500)

    # regist shared in local
    if request.get_json()['target'][:12] == "rs-elwebapi:":
        res_dict[res_id].shared.append(rs_config.el_agent_id)
        res_dict[res_id].proxy_share[policy_id] = {
            "target_type":request.get_json()['target_type'], 
            "target": request.get_json()['target'][12:]
            }
    else:
        res_dict[res_id].shared.append(request.get_json()['target'])
    
    return {'share': 'successed'}, 200


# {'policy_id': 'xxx'}
@app.route('/share/<hapi_res_type>/<hapi_res_id>', methods=['DELETE'], strict_slashes=False)
def hapi_unshare(hapi_res_type, hapi_res_id):

     # check user identity
    if 'Access-Token' not in request.headers:
        abort(401)

    # check policy id in request body
    if 'policy_id' not in request.get_json():
        abort(400)

    policy_id = request.get_json()['policy_id']

    result, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])
    if result != True:
        abort(401)

    # check resource exist or not
    result, res_id = find_res_by_type_id(hapi_res_type, hapi_res_id)
    if result != True:
        Log.error('not found resource {} {}'.format(hapi_res_type, hapi_res_id))
        abort(404)

    # check user owned resource
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        abort(401)
    
    if res_id not in list_own_resid:
        abort(401)

    result, list_policy = KeycloakAccess.check_resource_shared(request.headers['Access-Token'], res_id)
    if result != True:
        abort(500)
    
    shared_uid = ''
    for policy_info in list_policy:
        Log.debug('{}'.format(policy_info))
        if policy_id != policy_info['id'] :
            continue
        if rs_config.el_agent_name in policy_info['users']:
            shared_uid = rs_config.el_agent_id

    if shared_uid == '':
        Log.error('shared uid not found')
        abort(404)

    result, result_code = KeycloakAccess.unshare_resource(
        request.headers['Access-Token'], request.get_json()['policy_id'])
    if result != True:
        abort(result_code)

    res_dict[res_id].shared.remove(shared_uid)
    res_dict[res_id].proxy_share.pop(request.get_json()['policy_id'])

    return {'unshare': 'successed'}, 204



@app.route('/sharedWithMe', methods=['GET'], strict_slashes=False)
def hapi_sharedwithme():

    # check user identity
    if 'Access-Token' not in request.headers:
        abort(401)

    resule, uid, client = KeycloakAccess.token_get_uid(
        request.headers['Access-Token'])
    if resule == False:
        abort(401)

    # show shared with me for third party application
    if uid != rs_config.el_agent_id or client != 'pcha-rs':
        abort(401)

    return_list = []

    global res_dict
    for res_id in res_dict:
        if rs_config.el_agent_id not in res_dict[res_id].shared:
            continue
        return_list.append(res_dict[res_id].getInfo_share())

    # print({'resources': return_list})
    # return {'resources': return_list}
    return Response(json.dumps(return_list), mimetype='application/json')

def retuen_permisson_ticket(res_id):
    resule, ticket = KeycloakAccess.make_ticket(res_dict[res_id].res_id)
    if resule == False:
        Log.error('[create ticket] FIELD!!!')
        abort(401)
    
    return {
        'as_url': '{}:{}/realms/{}/protocol/openid-connect/token'.format(rs_config.am_host, rs_config.am_port, rs_config.realm_name),
        'ticket': ticket,
        'audience': rs_config.client_id,
        'authz_type': 'uma2.0'
    }, 401


def init(am_host, am_port, real_name, client_id, 
client_scret, hapi_host, hapi_port, el_agent_name, el_agent_id):
    rs_config.am_host = am_host
    rs_config.am_port = am_port
    rs_config.realm_name = real_name

    rs_config.client_id = client_id
    rs_config.client_screct = client_scret

    rs_config.hapi_host = hapi_host
    rs_config.hapi_port = hapi_port

    rs_config.el_agent_name = el_agent_name
    rs_config.el_agent_id = el_agent_id


def find_res_by_type_id(hapi_type, hapi_id):
    global res_dict
    for res_id in res_dict:
        if res_dict[res_id].hapi_res_type != hapi_type:
            continue

        if res_dict[res_id].hapi_res_id != hapi_id:
            continue

        return True, res_id

    return False, ''


def depend_server_check():
    while True:
        if KeycloakAccess.check_am_ready_uma() != True:
            Log.info('\tAM not ready')
            sleep(10)
            continue
        if HapiAccess.check_hapi_ready() != True:
            Log.info('\tHAPI not ready')
            sleep(10)
            continue

        break


def main(list_args):
    
    Log.info('[check server initialization parameters]')
    if not server_args_check(list_args):
        Log.info('usage:\n\tam_host am_port real_name client_id client_scret hapi_host hapi_port el_agent_name el_agnet_id')
        return

    Log.info('[initialization HAPI Resource server config]')
    init(list_args[1], list_args[2], list_args[3], list_args[4], 
        list_args[5], list_args[6], list_args[7], list_args[8], list_args[9])

    Log.info('parameters: \
        \n\tam_host: {} \n\tam_port: {} \
        \n\treal_name: {} \n\tclient_id: {} \
        \n\tclient_scret: {} \n\thapi_host: {} \
        \n\thapi_port: {} \n\tel_agent_name: {} \n\tel_agent_id: {}'.format(
        rs_config.am_host, rs_config.am_port,
        rs_config.realm_name, rs_config.client_id,
        rs_config.client_screct, rs_config.hapi_host,
        rs_config.hapi_port, rs_config.el_agent_name, rs_config.el_agent_id
    ))

    Log.info('[check depend server ready]')
    depend_server_check()

    Log.info('[start Resource server client token keeper]')
    start_keeper()

    Log.info('[start HAPI Resource server]')
    app.run(host='0.0.0.0', port='6000', debug=False)


def server_args_check(list_args):
    Log.debug('{}'.format(list_args))
    if len(list_args) != 10:
        return False
    if '.' not in list_args[1] or '.' not in list_args[6]:
        return False
    return True

if __name__ == '__main__':
    main(sys.argv)
