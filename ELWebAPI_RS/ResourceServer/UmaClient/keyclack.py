import requests
import Log
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

def get_oidc_wellknown(am_host, am_port, realm_name):
    url = 'https://{}:{}/realms/{}/.well-known/openid-configuration'.format(
        am_host, am_port, realm_name)

    Log.debug('[keyclack get_oidc_wellknown]\
        \n\turl: {}'.format(url))

    return requests.get(url, verify=False)

def get_uma_wellknown(am_host, am_port, realm_name):
    url = 'https://{}:{}/realms/{}/.well-known/uma2-configuration'.format(
        am_host, am_port, realm_name)

    Log.debug('[keyclack get_uma_wellknown]\
        \n\turl: {}'.format(url))

    return requests.get(url, verify=False)

# url: realms/{}/protocol/openid-connect/token
# post
# response:
#   access_token
#   expires_in
#   refresh_expires_in
#   refresh_token
#   token_type
#   id_token
#   not-before-policy
#   session_state
def get_client_token(am_host, am_port, realm_name, client_id, client_screct):
    url = 'https://{}:{}/realms/{}/protocol/openid-connect/token'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'client_id': client_id,
        'client_secret': client_screct,
        'grant_type': 'client_credentials',
    }

    Log.debug('[keyclack get_client_token]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, data=payload, verify=False)

def get_user_token(am_host, am_port, realm_name, client_id, client_screct, user_name, user_pw):
    url = 'https://{}:{}/realms/{}/protocol/openid-connect/token'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'client_id': client_id,
        'client_secret': client_screct,
        'username': user_name,
        'password': user_pw,
        'grant_type': 'password',
        'scope': 'openid',
    }

    Log.debug('[keyclack get_user_token]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, data=payload, verify=False)

def check_token(am_host, am_port, realm_name, client_id, client_screct, access_token):
    url = 'https://{}:{}/realms/{}/protocol/openid-connect/token/introspect'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'client_id': client_id,
        'client_secret': client_screct,
        'token': access_token,
    }

    Log.debug('[keyclack check_token]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, data=payload, verify=False)
# 
# Resource Management
# 

# /realms/{}/authz/protection/resource_set


# url: /realms/{}/authz/protection/resource_set
# post
# respose
#   name
#   owner {id, name}
#   ownerNAmagenAccess
#   _id
#   uris
#   resource_scopes
def resource_create(am_host, am_port, realm_name, client_token, res_name, res_owner):
    url = 'https://{}:{}/realms/{}/authz/protection/resource_set'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(client_token)
    }

    payload = {
        'name': res_name,
        'owner': res_owner,
        'ownerManagedAccess': True,
        'scopes': ["metadata", "data_read", "data_write"],
    }

    Log.debug('[keyclack resource_create]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, json=payload, verify=False)


def resource_read(am_host, am_port, realm_name, client_token, res_id):
    url = 'https://{}:{}/realms/{}/authz/protection/resource_set/{}'.format(
        am_host, am_port, realm_name, res_id)

    header = {
        'Authorization': 'Bearer {}'.format(client_token)
    }

    Log.debug('[keyclack resource_read]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url, headers=header, verify=False)

def resource_owner(am_host, am_port, realm_name, client_token, res_owner):
    url = 'https://{}:{}/realms/{}/authz/protection/resource_set?owner={}'.format(
        am_host, am_port, realm_name, res_owner)

    header = {
        'Authorization': 'Bearer {}'.format(client_token)
    }

    Log.debug('[keyclack resource_owner]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url, headers=header, verify=False)


def resource_delete(am_host, am_port, realm_name, client_token, res_id):
    url = 'https://{}:{}/realms/{}/authz/protection/resource_set/{}'.format(
        am_host, am_port, realm_name, res_id)

    header = {
        'Authorization': 'Bearer {}'.format(client_token)
    }

    Log.debug('[keyclack resource_delete]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.delete(url, headers=header, verify=False)

# url: /realms/{}/authz/protection/resource_set
# get
# response
#   []
def resource_list(am_host, am_port, realm_name, client_token):
    url = 'https://{}:{}/realms/{}/authz/protection/resource_set'.format(
        am_host, am_port, realm_name)

    header = {
        'Authorization': 'Bearer {}'.format(client_token)
    }

    Log.debug('[keyclack resource_list]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url, headers=header, verify=False)


# 
# Permission request
# 

# /realms/{}/authz/protection/permission

def permission_create_ticket(am_host, am_port, realm_name, client_token, res_id):
    url = 'https://{}:{}/realms/{}/authz/protection/permission'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(client_token)
    }

    payload = [
        {
            'resource_id': res_id,
            'resource_scopes': [
                'data_read'
            ],
        },
    ]

    Log.debug('[keyclack permission_create_ticket]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, json=payload, verify=False)

# def permossion_update_ticket():
#     return

# 
# Policy management
# 

# /realms/{}/authz/protection/uma-policy/{resource_id}

# {name:'', description:'', users:[], scopes:[]}
# share_type: user or clients
def policy_create(am_host, am_port, realm_name, user_token, res_id, share_type, share_target, desc=''):
    url = 'https://{}:{}/realms/{}/authz/protection/uma-policy/{}'.format(
        am_host, am_port, realm_name, res_id)

    header = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Authorization': 'Bearer {}'.format(user_token)
    }
    
    payload = {
        'name': "policy-{}-{}-{}-data_read".format(res_id, share_type, share_target),
        'description': "policy, target resource:, share with: {}({}), permission scope: data_read".format(res_id, share_target, share_type),
        share_type: [share_target],
        'scopes': ['data_read'],
        'description': desc
    }

    Log.debug('[keyclack policy_create]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, json=payload, verify=False)

def policy_create_with_name(am_host, am_port, realm_name, user_token, res_id, share_type, share_target, p_name,desc=''):
    url = 'https://{}:{}/realms/{}/authz/protection/uma-policy/{}'.format(
        am_host, am_port, realm_name, res_id)

    header = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Authorization': 'Bearer {}'.format(user_token)
    }
    
    payload = {
        'name': p_name,
        'description': "policy, target resource:, share with: {}({}), permission scope: data_read".format(res_id, share_target, share_type),
        share_type: [share_target],
        'scopes': ['data_read'],
        'description': desc
    }

    Log.debug('[keyclack policy_create]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, json=payload, verify=False)


# def policy_read(client):
#     url = 'https://{}:{}/realms/{}/authz/protection/uma-policy?{}={}'.format(
#         am_host, am_port, realm_name, search_type, search_target)

#     header = {
#         'Authorization': 'Bearer {}'.format(client_token)
#     }

#     Log.debug('[keyclack policy_search]')
#     Log.debug('\turl:', url)
#     Log.debug('\theader:', header)

#     return requests.get(url, headers=header) 

def policy_search(am_host, am_port, realm_name, user_token, search_type, search_target):
    url = 'https://{}:{}/realms/{}/authz/protection/uma-policy?{}={}'.format(
        am_host, am_port, realm_name, search_type, search_target)

    header = {
        'Authorization': 'Bearer {}'.format(user_token)
    }

    Log.debug('[keyclack policy_search]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url, headers=header, verify=False)

# def policy_update():
#     return

def policy_delete(am_host, am_port, realm_name, user_token, policy_id):
    url = 'https://{}:{}/realms/{}/authz/protection/uma-policy/{}'.format(
        am_host, am_port, realm_name, policy_id)

    header = {
        'Authorization': 'Bearer {}'.format(user_token)
    }

    Log.debug('[keyclack policy_delete]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.delete(url, headers=header, verify=False)

def policy_list_all(am_host, am_port, realm_name, user_token):
    url = 'https://{}:{}/realms/{}/authz/protection/uma-policy'.format(
        am_host, am_port, realm_name)

    header = {
        'Authorization': 'Bearer {}'.format(user_token)
    }

    Log.debug('[keyclack policy_list_all]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url, headers=header, verify=False)


# 
# Requesting Party Token
# 

# realms/{}/protocol/openid-connect/token/introspect
def rpt_check(am_host, am_port, realm_name, client_id, client_screct, rpt):
    url = 'https://{}:{}/realms/{}/protocol/openid-connect/token/introspect'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'token_type_hint': 'requesting_party_token',
        'token': rpt,
        'client_id': client_id,
        'client_secret': client_screct
    }

    Log.debug('[keyclack rpt_check]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, data=payload, verify=False)


# realms/{}/protocol/openid-connect/token

def rpt_get(am_host, am_port, realm_name, client_id, requester_token, permission_ticket):
    url = 'https://{}:{}/realms/{}/protocol/openid-connect/token'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(requester_token)
    }

    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
        'audience': client_id,
        'ticket': permission_ticket
    }

    Log.debug('[keyclack rpt_get]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, data=payload, verify=False)


def user_logout(am_host, am_port, realm_name, client_id, client_screct, refresh_token):
    url = 'https://{}:{}/realms/{}/protocol/openid-connect/logout'.format(
        am_host, am_port, realm_name)

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'client_id': client_id,
        'client_secret': client_screct,
        'refresh_token': refresh_token,
    }

    Log.debug('[keyclack user_logpit]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url,header,payload))

    return requests.post(url, headers=header, data=payload, verify=False)