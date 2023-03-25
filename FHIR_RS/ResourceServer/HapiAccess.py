import HapiClient
import rs_config

import Log

# logging.basicConfig(level=logging.DEBUG)

def check_hapi_ready() -> bool:
    try:
        response = HapiClient.resource_list_up(rs_config.hapi_host, rs_config.hapi_port, "Patient")
        Log.print_response(response)
        return True
    except:
        return False

def search_resource(res_type, req_header, search_parameters: dict):
    response = HapiClient.resource_search(
        rs_config.hapi_host, rs_config.hapi_port,
        res_type, req_header, search_parameters)
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    return True, response.json()

def search_patient_id(req_header, uid):
    response = HapiClient.resource_search(
        rs_config.hapi_host, rs_config.hapi_port,
        "Patient", req_header, {"identifier": uid})
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    pid_list = []
    for patient_info in response.json()['entry']:
        print(patient_info['resource']['id'])
        pid_list.append(patient_info['resource']['id'])

    return True, pid_list



def get_resource(res_type, res_id, req_header):
    response = HapiClient.resource_get(
        rs_config.hapi_host, rs_config.hapi_port,
        res_type, res_id, req_header)
    Log.print_response(response)

    return response


def create_resource(res_type, req_header, req_content):
    response = HapiClient.resource_create(
        rs_config.hapi_host, rs_config.hapi_port,
        res_type, req_header, req_content)
    Log.print_response(response)

    if response.status_code != 201:
        return False, response.json()['resourceType'], response.json()['id'], response

    return True, response.json()['resourceType'], response.json()['id'], response


def delete_resource(res_type, res_id, req_header):
    response = HapiClient.resource_delete(
        rs_config.hapi_host, rs_config.hapi_port,
        res_type, res_id, req_header)
    Log.print_response(response)

    if response.status_code != 200:
        return False, ''

    if 'Successfully deleted' not in response.json()['issue'][0]['diagnostics']:
        return False

    return True, response
