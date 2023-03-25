import requests
import Log

import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

def resource_list_up(host_address, host_port, res_type):
    url = 'http://{}:{}/fhir/{}'.format(
        host_address, host_port, res_type)

    Log.debug('[hapi resource_list_up]\
        \n\turl: {}'.format(url))

    return requests.get(url)

def resource_get(host_address, host_port, res_type, res_id, req_header):
    url = 'http://{}:{}/fhir/{}/{}'.format(
        host_address, host_port, res_type, res_id)

    Log.debug('[hapi resource_get]\
        \n\turl: {}\
        \n\theader: {}'.format(url, req_header))

    return requests.get(url, headers=req_header)


def resource_search(host_address, host_port, res_type, req_header, search_parameters: dict):
    url = 'http://{}:{}/fhir/{}'.format(
        host_address, host_port, res_type)

    search_parameters['_count'] = 300

    Log.debug('[hapi resource_search]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tparameters: {}'.format(url, req_header, search_parameters))

    return requests.get(url, headers=req_header, params=search_parameters)


def resource_create(host_address, host_port, res_type, req_header, req_content):
    url = 'http://{}:{}/fhir/{}'.format(
        host_address, host_port, res_type)

    Log.debug('[hapi resource_create]\
        \n\turl: {}\
        \n\theader: {}\
        \n\tpayload: {}'.format(url, req_header, req_content))

    return requests.post(url, headers=req_header, json=req_content)


def resource_delete(host_address, host_port, res_type, res_id, req_header):
    url = 'http://{}:{}/fhir/{}/{}'.format(
        host_address, host_port, res_type, res_id)

    Log.debug('[hapi resource_delete]\
        \n\turl: {}\
        \n\theader: {}'.format(url, req_header))

    return requests.post(url, headers=req_header)