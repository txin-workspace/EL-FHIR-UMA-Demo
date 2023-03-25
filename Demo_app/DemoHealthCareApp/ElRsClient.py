import requests
import Log

def check_rs_ready(rs_host, rs_port):
    url = 'http://{}:{}/'.format(rs_host, rs_port)

    Log.debug('[check_rs_ready]\
        \n\turl: {}'.format(url))

    return requests.get(url=url)

def get_dev_info(rs_host, rs_port, access_token):
    url = 'http://{}:{}/elapi/v1/devices'.format(rs_host, rs_port)

    header = {
        'Access-Token': '{}'.format(access_token)
    }

    Log.debug('[get_dev_info]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url=url, headers=header, verify=False)



def get_dev_ticket(rs_host, rs_port, device_id):
    url = 'http://{}:{}/elapi/v1/devices/{}/properties'.format(rs_host, rs_port, device_id)

    Log.debug('[get_dev_props]\
        \n\turl: {}'.format(url))

    return requests.get(url=url, verify=False)



def get_dev_props(rs_host, rs_port, rpt, device_id):
    url = 'http://{}:{}/elapi/v1/devices/{}/properties'.format(rs_host, rs_port, device_id)

    header = {
        'RPT': '{}'.format(rpt)
    }

    Log.debug('[get_dev_props]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url=url, headers=header, verify=False)



def get_health_info(rs_host, rs_port, access_token):
    url = 'http://{}:{}/elapi/v1/healthCareRecords'.format(rs_host, rs_port)

    header = {
        'Access-Token': '{}'.format(access_token)
    }

    Log.debug('[get_health_info]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url=url, headers=header, verify=False)



def get_health_ticket(rs_host, rs_port, health_id):
    url = 'http://{}:{}/elapi/v1/healthCareRecords/{}/properties'.format(rs_host, rs_port, health_id)

    Log.debug('[get_health_ticket]\
        \n\turl: {}'.format(url))

    return requests.get(url=url, verify=False)



def get_health_props(rs_host, rs_port, rpt, health_id):
    url = 'http://{}:{}/elapi/v1/healthCareRecords/{}/properties'.format(rs_host, rs_port, health_id)

    header = {
        'RPT': '{}'.format(rpt)
    }

    Log.debug('[get_health_props]\
        \n\turl: {}\
        \n\theader: {}'.format(url, header))

    return requests.get(url=url, headers=header, verify=False)


def get_rpt(url, audience, ticket, access_token):

    url = 'https://{}'.format(url)

    header = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
        'audience': audience,
        'ticket': ticket,
    }

    Log.debug('[get_rpt]\
        \n\turl: {}\
        \n\theader: {}\
        \b\tpayload: {}'.format(url, header, data))

    return requests.post(url=url, headers=header, data=data, verify=False)