import requests
import Log
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

def check_rs_ready(rs_host, rs_port):
    url = 'http://{}:{}/'.format(rs_host, rs_port)

    Log.debug('[check_rs_ready]\
        \n\turl: {}'.format(url))

    return requests.get(url=url)



def get_access_token(rs_host, rs_port, user_name, user_pw):
    url = 'http://{}:{}/login'.format(rs_host, rs_port)

    payload = {
        'user_id': user_name,
        'user_password': user_pw
    }

    Log.debug('[get_access_token]\
        \n\turl: {}\
        \n\tpayload: {}'.format(url, payload))

    return requests.post(url=url, json=payload)



def get_share_with_me(rs_host, rs_port, access_token):
    url = 'http://{}:{}/sharedWithMe'.format(rs_host, rs_port)

    header = {
        'Access-Token': access_token
    }

    Log.debug('[get_share_with_me]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url=url, headers=header)



def get_res_ticket(rs_host, rs_port, fhir_res_type, fhir_res_id):
    url = 'http://{}:{}/fhir/{}/{}'.format(
        rs_host, rs_port, fhir_res_type, fhir_res_id)

    Log.debug('[get_res_ticket]\
        \n\turl: {}'.format(url))

    return requests.get(url=url)



def get_rpt(rs_am_url, rs_audience, res_ticket, access_token):
    url = 'https://{}'.format(rs_am_url)

    header = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
        'audience': rs_audience,
        'ticket': res_ticket
    }

    Log.debug('[get_rpt]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url, header, payload))

    return requests.post(url=url, headers=header, data=payload, verify=False)



def get_fhir_resource(rs_host, rs_port, fhir_res_type, fhir_res_id, rpt):
    url = 'http://{}:{}/fhir/{}/{}'.format(
        rs_host, rs_port, fhir_res_type, fhir_res_id)

    header = {
        'RPT': rpt
    }

    Log.debug('[get_fhir_resource]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url=url, headers=header)