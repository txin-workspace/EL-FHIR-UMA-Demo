from flask import Blueprint
from flask import request
from flask import abort

import json
import base64

# import Device
import KeycloakAccess
import rs_config
import Log
import re


device_api = Blueprint('device_api', __name__)

device_dict = {}

class Device:
    def __init__(self) -> None:
        self.id = ''
        self.description = {}
        self.prop_list = {}

        # uma resource id
        self.resource_id = None

        # shared user name list
        # {uid, pid}
        self.shared = []

    def print_me(self):
        return self.prop_list

    def check_shared(self, uname):
        for shared_info in self.shared:
            if uname == shared_info['uid']:
                return True

        return False


@device_api.errorhandler(401)
def not_found(error):
    return {"type": "referenceError", "message": "Token not allowed"}, 401


@device_api.errorhandler(404)
def not_found(error):
    return {"type": "referenceError", "message": "HTTP method or path is wrong"}, 404


# /
# get all debvices info

# /<device id>
# get one device description

# /<device id>/properites
# get one device all properties

# /<device id>/properites/<properties name>
# get one device s one property

@device_api.route('/', methods=['GET'], strict_slashes=False)
def testAPI_devices():

    if 'Access-Token' not in request.headers:
        abort(401)

    resule, uname, client = KeycloakAccess.token_get_uname(request.headers['Access-Token'])

    if resule == False:
        abort(401)

    return_list = []

    # show shared with me for third party application
    if client not in [rs_config.client_id, rs_config.web_client_id]:
        for dev_id in device_dict:
            if  device_dict[dev_id].check_shared(uname) == True:
                return_list.append(make_device_info(dev_id))

    # show my owned
    elif client == rs_config.web_client_id:
        result, list_own_resid = KeycloakAccess.check_own_resource(uname)
        if result != True:
            Log.error('[get owner resource] FIELD!!')

        else:
            for resid in list_own_resid:
                for dev_id in device_dict:
                    if device_dict[dev_id].resource_id != resid:
                        continue

                    return_list.append(make_device_info(dev_id))

    # show all i can access 
    elif client == rs_config.client_id:
        result, list_own_resid = KeycloakAccess.check_own_resource(uname)
        if result != True:
            Log.error('[get owner resource] FIELD!!')

        else:
            for resid in list_own_resid:
                for dev_id in device_dict:
                    if device_dict[dev_id].resource_id == resid or device_dict[dev_id].check_shared(uname) == True:
                        return_list.append(make_device_info_owner(dev_id, resid))
    
    return {
        'devices': return_list,
        "hasMore": False,
        "limit": 255,
        "offset": 0
    }


@device_api.route('/<device_id>', methods=['GET'], strict_slashes=False)
def testApi_one_desc(device_id):
    # TODO
    return abort(404)


@device_api.route('/<device_id>/properties', methods=['GET'], strict_slashes=False)
def testAPI_search(device_id):
    
    # device id not exist
    if device_id not in device_dict:
        abort(404)

    # no RPT and no access token , return ticket
    if 'RPT' not in request.headers and 'Access-Token' not in request.headers:
        Log.info('[no rpt and no access token] return ticket')
        return retuen_permisson_ticket(device_id)

    # has rpt, check rpt, 
    # if not active return ticket, else check detail, 
    if 'RPT' in request.headers:
        resule, rpt_detail = KeycloakAccess.check_rpt(request.headers['RPT'])

        if resule == False:
            Log.error('[check rpt] FIELD!!!')
            return retuen_permisson_ticket(device_id)
        
        if rpt_detail['active'] == False:
            Log.info('[check rpt] rpt not active')
            return retuen_permisson_ticket(device_id)

        # all pass, find device, and return
        for p in rpt_detail['permissions']:
            if 'data_read' not in p['scopes']:
                continue
            if p['resource_id'] != device_dict[device_id].resource_id:
                continue
            return device_dict[device_id].print_me()

    # if not for access and have Access-Token
    if 'RPT' not in request.headers and 'Access-Token' in request.headers:
        resule, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])

        if resule == False:
            abort(401)

        # not allow for third party application
        if client not in [rs_config.client_id, rs_config.web_client_id]:
            abort(401)

        # check my own
        result, list_own_resid = KeycloakAccess.check_own_resource(uid)
        if result != True:
            Log.error('[get owner resource] FIELD!!')
            abort(401)

        # not owner
        if device_dict[device_id].resource_id not in list_own_resid:
            abort(401)

        # all pass, return device properties
        return device_dict[device_id].print_me()

    abort(500)


# {dname: dvalue, dname: dvalue , -------}
@device_api.route('/<device_id>/properties', methods=['POST'], strict_slashes=False)
def testAPI_create(device_id):

    if device_id in device_dict:
        abort(500)

    resule, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])

    if resule == False:
        Log.error('[register device] check token FIELD!!!')
        abort(401)

    # not allow for third party application
    if client != rs_config.client_id:
        Log.info('[register device] client not allow')
        abort(401)

    # create resource and get resource id
    resule, res_id = KeycloakAccess.create_resource(device_id, uid)
    if resule == False:
        Log.error('[register device] create resource FIELD!!!')
        abort(500)

    # add properties to dict
    request_data = request.get_json()
    d = Device()
    d.id = device_id
    d.resource_id = res_id
    for name, value in request_data.items():
        # d.prop_list.append({name: value})
        d.prop_list[name] = value

    device_dict[device_id] = d

    return {'add Device': 'success'}, 200


@device_api.route('/share/<device_id>/properties', methods=['POST'], strict_slashes=False)
def testAPI_share_resource(device_id):
    # device id not exist
    if device_id not in device_dict:
        abort(404)

    # if Access-Token in header
    if 'Access-Token' not in request.headers:
        abort(401)

    # check user token
    resule, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])

    if resule == False:
        abort(401)

    # not allow for third party application
    if client not in [rs_config.client_id, rs_config.web_client_id]:
        abort(401)

    # check my own
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        Log.error('[get owner resource] FIELD!!')
        abort(401)

    # not owner
    if device_dict[device_id].resource_id not in list_own_resid:
        abort(401)

    # all pass, create policy
    # check payload
    if 'target' not in request.get_json() or 'target_type' not in request.get_json():
        abort(500)

    result, p_id = KeycloakAccess.share_resource(
        request.headers['Access-Token'], device_dict[device_id].resource_id,
        request.get_json()['target_type'], request.get_json()['target']
    )

    # Log.warning('{}  {}'.format(result, p_id))

    if result != True:
        Log.error('[create policy] FIELD!!!')
        abort(500)

    device_dict[device_id].shared.append(
        {
            'uid': request.get_json()['target'],
            'pid': p_id
        }
    )
    
    return 'successed', 200


@device_api.route('/share/<device_id>/properties', methods=['DELETE'], strict_slashes=False)
def testAPI_unshare_resource(device_id):
    # device id not exist
    if device_id not in device_dict:
        abort(404)

    # if Access-Token in header
    if 'Access-Token' not in request.headers:
        abort(401)

    # check user token
    resule, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])

    if resule == False:
        abort(401)

    # not allow for third party application
    if client not in [rs_config.client_id, rs_config.web_client_id]:
        abort(401)

    # check my own
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        Log.error('[get owner resource] FIELD!!')
        abort(401)

    # not owner
    if device_dict[device_id].resource_id not in list_own_resid:
        abort(401)

    # all pass, delete policy
    # check payload
    if 'policy_id' not in request.get_json():
        abort(400)

    result, s_code = KeycloakAccess.unshare_resource(
        request.headers['Access-Token'], request.get_json()['policy_id']
    )

    # Log.warning('{}  {}'.format(result, p_id))

    if result != True:
        Log.error('[delete policy] FIELD!!!')
        abort(s_code)

    Log.warning('{}'.format(device_dict[device_id].shared))
    # Log.warning('{}'.format(
    #     {
    #         'uid': get_uname_from_jwt(request.headers['Access-Token']),
    #         'pid': request.get_json()['policy_id']
    #     }
    # ))

    for n in range(len(device_dict[device_id].shared)):

        if device_dict[device_id].shared[n]['pid'] != request.get_json()['policy_id']:
            continue

        Log.warning('{}'.format(device_dict[device_id].shared.pop(n)))
        break

    
    return 'successed', 200
    
        

@device_api.route('/<device_id>/properties/<prop_name>', methods=['GET'], strict_slashes=False)
def testAPI_search_one(device_id, prop_name):

    # device id not exist
    if device_id not in device_dict:
        abort(404)

    # no rpt and no access token , return ticket
    if 'RPT' not in request.headers and 'Access-Token' not in request.headers:
        Log.info('[no rpt and no access token] return ticket')
        return retuen_permisson_ticket(device_id)

    # has rpt, check rpt, 
    # if not active return ticket, else check detail, 
    if 'RPT' in request.headers:
        resule, rpt_detail = KeycloakAccess.check_rpt(request.headers['RPT'])

        if resule == False:
            Log.error('[check rpt] FIELD!!!')
            return retuen_permisson_ticket(device_id)
        
        if rpt_detail['active'] == False:
            Log.info('[check rpt] rpt not active')
            return retuen_permisson_ticket(device_id)
        # all pass, find device, and return
        for p in rpt_detail['permissions']:
            if 'data_read' not in p['scopes']:
                continue
            if p['resource_id'] != device_dict[device_id].resource_id:
                continue
            if prop_name not in device_dict[device_id].prop_list:
                abort(404)
            return {prop_name: device_dict[device_id].prop_list[prop_name]}

    # if not for access and have Access-Token
    if 'RPT' not in request.headers and 'Access-Token' in request.headers:
        resule, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])

        if resule == False:
            abort(401)

        # not allow for third party application
        if client not in [rs_config.client_id, rs_config.web_client_id]:
            abort(401)

        # check my own
        result, list_own_resid = KeycloakAccess.check_own_resource(uid)
        if result != True:
            Log.error('[get owner resource] FIELD!!')
            abort(401)

        # not owner
        if device_dict[device_id].resource_id not in list_own_resid:
            abort(401)

        # all pass, return device properties
        return {prop_name: device_dict[device_id].prop_list[prop_name]}

    
# {prop_name: new_value}
@device_api.route('/<device_id>/properties/<prop_name>', methods=['PUT'], strict_slashes=False)
def testAPI_update_one(device_id, prop_name):

    # device id not exist
    if device_id not in device_dict:
        abort(404)

    # if Access-Token in header
    if 'Access-Token' not in request.headers:
        abort(401)

    # check user token
    resule, uid, client = KeycloakAccess.token_get_uid(request.headers['Access-Token'])

    if resule == False:
        abort(401)

    # not allow for third party application
    if client != rs_config.client_id:
        abort(401)

    # check my own
    result, list_own_resid = KeycloakAccess.check_own_resource(uid)
    if result != True:
        Log.error('[get owner resource] FIELD!!')
        abort(401)

    # not owner
    if device_dict[device_id].resource_id not in list_own_resid:
        abort(401)

    # all pass, create policy
    request_data = request.get_json()

    if prop_name not in request_data:
        abort(500)

    if prop_name not in device_dict[device_id].prop_list:
        abort(500)

    if type(request_data[prop_name]) != type(device_dict[device_id].prop_list[prop_name]):
        abort(500)

    device_dict[device_id].prop_list[prop_name] = request_data[prop_name]

    return {prop_name: device_dict[device_id].prop_list[prop_name]}



def make_device_info(dev_id):
    dev_info = {
        'id': dev_id,
        'deviceType': re.sub('\d', '', dev_id),
        "protocol": {"type": "ECHONET_Lite v1.1", "version": "Rel.A"},
        'manufacturer': device_dict[dev_id].prop_list['manufacturer']
    }

    if 'co2Sensor' in dev_id:
        dev_info['deviceType'] = 'co2Sensor'

    return dev_info

def make_device_info_owner(dev_id, res_id):
    dev_info = {
        'id': dev_id,
        'deviceType': re.sub('\d', '', dev_id),
        "protocol": {"type": "ECHONET_Lite v1.1", "version": "Rel.A"},
        'manufacturer': device_dict[dev_id].prop_list['manufacturer'],
        'type': 'own' if device_dict[dev_id].resource_id == res_id else 'shared',
    }

    if dev_info['type'] == 'own':
        dev_info['shared'] = device_dict[dev_id].shared

    if 'co2Sensor' in dev_id:
        dev_info['deviceType'] = 'co2Sensor'

    return dev_info



def retuen_permisson_ticket(device_id):
    resule, ticket = KeycloakAccess.make_ticket(device_dict[device_id].resource_id)
    if resule == False:
        Log.error('[create ticket] FIELD!!!')
        abort(401)
    
    return {
        'as_url': '{}:{}/realms/{}/protocol/openid-connect/token'.format(
            rs_config.am_host, rs_config.am_port, rs_config.realm_name),
        'ticket': ticket,
        'audience': rs_config.client_id,
        'authz_type': 'uma2.0'
    }, 401



def get_uname_from_jwt(jwt):
    rpt_body = jwt.split('.')[1]
    rpt_body += '=' *(4 - len(rpt_body) % 4)
    return json.loads(base64.b64decode(rpt_body).decode())['preferred_username']