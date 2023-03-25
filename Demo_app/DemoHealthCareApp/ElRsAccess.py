import app_config
import ElRsClient
import Log



def check_rs_ready() -> bool:
    try:
        resp = ElRsClient.check_rs_ready(
            app_config.rs_host, app_config.rs_port)
    except:
        return False
    
    Log.print_response(resp)

    if resp.status_code != 200:
        return False

    return True



def get_dev_info(access_token):
    resp = ElRsClient.get_dev_info(
        app_config.rs_host, app_config.rs_port, access_token
    )
    Log.print_response(resp)

    if resp.status_code != 200:
        Log.error('get_dev_info field!!')
        return False, ''

    return True, resp.json()['devices']



def get_dev_ticket(el_id):
    resp = ElRsClient.get_dev_ticket(
        app_config.rs_host, app_config.rs_port, el_id
    )
    Log.print_response(resp)
    
    if resp.status_code != 401:
        Log.error('get_dev_ticket field!!')
        return False, ''

    return True, resp.json()



def get_dev_props(rpt, el_id):
    resp = ElRsClient.get_dev_props(
        app_config.rs_host, app_config.rs_port, rpt, el_id
    )
    Log.print_response(resp)
    
    if resp.status_code != 200:
        Log.error('get_dev_props field!!')
        return False, ''

    return True, resp.json()



def get_health_info(access_token):
    resp = ElRsClient.get_health_info(
        app_config.rs_host, app_config.rs_port, access_token
    )
    Log.print_response(resp)
    
    if resp.status_code != 200:
        Log.error('get_health_info field!!')
        return False, ''

    return True, resp.json()['healthCareRecorders']



def get_health_ticket(el_id):
    resp = ElRsClient.get_health_ticket(
        app_config.rs_host, app_config.rs_port, el_id
    )
    Log.print_response(resp)
    
    if resp.status_code != 401:
        Log.error('get_health_ticket field!!')
        return False, ''

    return True, resp.json()  



def get_health_props(rpt, el_id):
    resp = ElRsClient.get_health_props(
        app_config.rs_host, app_config.rs_port, rpt, el_id
    )
    Log.print_response(resp)
    
    if resp.status_code != 200:
        Log.error('get_health_props field!!')
        return False, ''

    return True, resp.json()   



def get_rpt(url, audience, ticket, access_token):
    resp = ElRsClient.get_rpt(
        url, audience, ticket, access_token 
    )
    Log.debug(resp)

    if resp.status_code != 200:
        Log.error('get_health_props field!!')
        return False, ''

    return True, resp.json()



def get_el_dev(access_token):
    
    result, dev_info_list = get_dev_info(access_token)
    if result != True:
        return []

    for dev_info in dev_info_list:
        result, ticket_info_dict = get_dev_ticket(dev_info['id'])
        if result != True:
            continue

        result, rpt_detail_dict = get_rpt(
            ticket_info_dict['as_url'], ticket_info_dict['audience'],
            ticket_info_dict['ticket'], access_token)
        if result != True:
            continue

        result, dev_prop_dict = get_dev_props(
            rpt_detail_dict['access_token'], dev_info['id'])
        if result != True:
            continue

        dev_info['properties'] = dev_prop_dict

    return dev_info_list



def get_el_health(access_token):
    result, health_info_list = get_health_info(access_token)
    if result != True:
        return []

    for health_info in health_info_list:
        result, ticket_info_dict = get_health_ticket(health_info['id'])
        if result != True:
            continue

        result, rpt_detail_dict = get_rpt(
            ticket_info_dict['as_url'], ticket_info_dict['audience'],
            ticket_info_dict['ticket'], access_token)
        if result != True:
            continue

        result, dev_prop_dict = get_health_props(
            rpt_detail_dict['access_token'], health_info['id'])
        if result != True:
            continue

        health_info['properties'] = dev_prop_dict

    return health_info_list