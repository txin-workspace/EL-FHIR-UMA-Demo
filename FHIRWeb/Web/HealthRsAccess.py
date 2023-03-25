import web_config
import HealthRsClient
# import TokenKeeper
import Log

def check_rs_ready() -> bool:
    try:
        resp = HealthRsClient.check_rs_ready(
            web_config.health_rs_host, web_config.health_rs_port)
    except:
        return False
    
    Log.print_response(resp)

    if resp.status_code != 200:
        return False

    return True


def get_user_token(user_name, user_password):
    resp = HealthRsClient.get_access_token(
        web_config.health_rs_host, web_config.health_rs_port, 
        user_name, user_password
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        return False, '', ''

    return True, resp.json()['access_token'], resp.json()['expires_in']

def get_sharewithme(access_token):
    resp = HealthRsClient.get_share_with_me(
        web_config.health_rs_host, web_config.health_rs_port, 
        access_token
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        return False, ''

    return True, resp.json()


# rpt need 
def get_resource_value(rpt, resource_type, resource_id, prop_name_list: list):
    resp = HealthRsClient.get_fhir_resource(
        web_config.health_rs_host, web_config.health_rs_port,
        resource_type, resource_id, rpt
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        return False, ''
    
    if resource_type == 'Patient':
        return True, cover_fhir_patient(prop_name_list, resp.json())

    elif resource_type == 'Observation':
        return True, conver_fhir_observation(prop_name_list[0], resp.json())



def get_resource_ticket(resource_type, resource_id):
    resp = HealthRsClient.get_res_ticket(
        web_config.health_rs_host, web_config.health_rs_port,
        resource_type, resource_id
    )
    Log.print_response(resp)

    return resp
    
def get_resource_ticket_checked(resource_type, resource_id):
    resp = HealthRsClient.get_res_ticket(
        web_config.health_rs_host, web_config.health_rs_port,
        resource_type, resource_id
    )
    Log.print_response(resp)

    if resp.status_code != 401:
        Log.error('[get_resource_ticket_checked] \
            get health rs ticket failed! {} {}'.format(
                resource_type, resource_id
        ))
        return False, ''

    resp_detail = resp.json()
    if 'ticket' not in resp_detail \
        or 'as_url' not in resp_detail \
            or 'audience' not in resp_detail:

        Log.error('[get_resource_ticket_checked] \
            get health rs ticket failed! \
                response wrong ! - {} {}'.format(
                resource_type, resource_id
        ))
        return False, ''

    return True, resp_detail

# def get_rpt(health_am_url, ticket, audience):
#     resp = HealthRsClient.get_rpt(
#         health_am_url, audience, ticket, 
#         TokenKeeper.health_rs_agent_token
#     )
#     Log.print_response(resp)

#     if resp.status_code != 200:
#         return False, ''

#     return True, resp.json()


def cover_fhir_patient(prop_name_list, fhir_patient):
    dict_prop_value = {}
    for prop_name in prop_name_list:
        if prop_name == 'age':
            dict_prop_value[prop_name] = 2023 - int(fhir_patient['birthDate'].split('-')[0])
        # elif prop_name == 'id':
        #     dict_prop_value[prop_name] = fhir_patient['id']
        else:
            dict_prop_value[prop_name] = fhir_patient[prop_name]

    return dict_prop_value



def conver_fhir_observation(prop_name, fhir_observation):
    dict_prop_value = {}
    if prop_name == 'bloodPressure':
        dict_prop_value[prop_name] = [0, 0]
        if 'component' not in fhir_observation:
            return dict_prop_value

        for comp in fhir_observation['component']:
            if comp['code']['coding'][0]['code'] == '8480-6':
                dict_prop_value[prop_name][1] = comp['valueQuantity']['value']
            elif comp['code']['coding'][0]['code'] == '8462-4':
                dict_prop_value[prop_name][0] = comp['valueQuantity']['value']

    else:
        p_name = loinc_code_conver(fhir_observation['code']['coding'][0]['code'])
        if p_name == '':
            return dict_prop_value

        if p_name != prop_name:
            return dict_prop_value

        dict_prop_value[prop_name] = fhir_observation['valueQuantity']['value']

    return dict_prop_value



def loinc_code_conver(code):
    Log.debug('[loinc_code_conver] {}'.format(code))
    if code == '8310-5':
        return 'bodyTemperature'

    elif code == '29463-7':
        return 'bodyWeight'

    elif code == '39156-5':
        return 'bmi'

    # elif code == '8480-6':
    #     return 'bloodPressure-s'

    # elif code == '8462-4':
    #     return 'bloodPressure-d'

    elif code == '8867-4':
        return 'heartRate'
    
    elif code == '59408-5':
        return 'pulseOximetry'

    else:
        Log.warning('[loinc_code_conver] other: {}'.format(code))
        return ''


def get_fhir_patient_res_list(access_token):
    resp = HealthRsClient.get_fhir_resource_list(
        web_config.health_rs_host, web_config.health_rs_port, 'Patient', access_token
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        Log.error('get_fhir_patient_res_list field')
        return False, ''

    return True, resp.json()


def get_fhir_observation_list(access_token):
    resp = HealthRsClient.get_fhir_resource_list(
        web_config.health_rs_host, web_config.health_rs_port, 'Observation', access_token
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        Log.error('get_fhir_patient_res_list field')
        return False, ''

    return True, resp.json()


def share_res(res_type, res_id, access_token, target_user):
    resp = HealthRsClient.share_res(
        web_config.health_rs_host, web_config.health_rs_port,
        res_type, res_id, access_token, target_user
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        Log.error('share resource field')
        return False

    return True


def unshare_res(res_type, res_id, access_token, policy_id):
    resp = HealthRsClient.unshare_res(
        web_config.health_rs_host, web_config.health_rs_port,
        res_type, res_id, access_token, policy_id
    )
    Log.print_response(resp)

    if resp.status_code != 204:
        Log.error('un share resource field')
        return False

    return True