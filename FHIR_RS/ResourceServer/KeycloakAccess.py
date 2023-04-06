import UmaClient.keyclack
import rs_config
import TokenKeeper

import Log

def check_am_ready_oidc() -> bool:
    try:
        response = UmaClient.keyclack.get_oidc_wellknown(rs_config.am_host, rs_config.am_port, rs_config.realm_name)
        Log.print_response(response)
        return True
    except:
        return False

def check_am_ready_uma() -> bool:
    try:
        response = UmaClient.keyclack.get_uma_wellknown(rs_config.am_host, rs_config.am_port, rs_config.realm_name)
        Log.print_response(response)
        return True
    except:
        return False

def get_client_token():
    response = UmaClient.keyclack.get_client_token(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name, 
        rs_config.client_id, rs_config.client_screct)
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    return True, response.json()['access_token']

def get_user_token(user_id, user_password):
    response = UmaClient.keyclack.get_user_token(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        rs_config.client_id, rs_config.client_screct, 
        user_id, user_password)
    Log.print_response(response)

    # if response.status_code != 200:
    #     return False, ''

    # return True, response
    return response

def token_get_uid(header_auth: str):
    response = UmaClient.keyclack.check_token(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        rs_config.client_id, rs_config.client_screct, 
        header_auth.replace('Bearer ',''))
    Log.print_response(response)

    if response.status_code != 200:
        return False, '', ''

    if response.json()['active'] != True:
        return False, '', ''
    
    return True, response.json()['sub'], response.json()['azp']

def check_rpt(header_auth: str):
    response = UmaClient.keyclack.rpt_check(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        rs_config.client_id, rs_config.client_screct, 
        header_auth.replace('Bearer ',''))
    Log.print_response(response)

    if response.status_code != 200:
        Log.info('[check rpt] am access not ok')
        return False, ''

    if response.json()['active'] != True:
        Log.info('[check rpt] rpt not active')
        return False, ''

    return True, response.json()

def make_ticket(resource_id):
    response = UmaClient.keyclack.permission_create_ticket(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        TokenKeeper.client_token, resource_id)
    Log.print_response(response)

    if response.status_code != 201:
        return False, ''

    return True, response.json()['ticket']

def check_own_resource(user_id):
    response = UmaClient.keyclack.resource_owner(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        TokenKeeper.client_token, user_id)
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    return True, response.json()
    
def create_resource(res_name, user_id):
    response = UmaClient.keyclack.resource_create(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        TokenKeeper.client_token, res_name, user_id)
    Log.print_response(response)

    if response.status_code != 201:
        return False, ''

    return True, response.json()['_id']

def delete_resource(res_id):
    response = UmaClient.keyclack.resource_delete(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        TokenKeeper.client_token, res_id)
    Log.print_response(response)

    if response.status_code != 204:
        return False

    return True

def share_resource(header_auth: str, res_id, share_type, target_user):
    if share_type == 'user':
        response = UmaClient.keyclack.policy_create(
            rs_config.am_host, rs_config.am_port, rs_config.realm_name,
            header_auth.replace('Bearer ',''), res_id, 'users', target_user)

    elif share_type == 'client':
        response = UmaClient.keyclack.policy_create(
            rs_config.am_host, rs_config.am_port, rs_config.realm_name,
            header_auth.replace('Bearer ',''), res_id, 'clients', target_user)

    else:
        return False, ''
        
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    return True, response.json()['id']

def share_resource_hapi(header_auth: str, res_id, share_type, target_user):
    if share_type not in ['user', 'client']:
        return False, ''

    response = UmaClient.keyclack.policy_create_proxy(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        header_auth.replace('Bearer ',''), res_id,
        'users', rs_config.el_agent_id,
        target_user)
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    return True, response.json()['id']

def unshare_resource(header_auth: str, policy_id):
    response = UmaClient.keyclack.policy_delete(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        header_auth.replace('Bearer ',''), policy_id)
    Log.print_response(response)

    if response.status_code != 204:
        return False, response.status_code

    return True, ''

def check_resource_shared(header_auth: str, res_id):
    response = UmaClient.keyclack.policy_search(
        rs_config.am_host, rs_config.am_port, rs_config.realm_name,
        header_auth.replace('Bearer ',''), "resource", res_id)
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    return True, response.json()
