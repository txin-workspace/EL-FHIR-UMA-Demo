import requests
import Log
import sys
import os
import json
import time

rs_host=''
rs_port=''
rs_uname=''
rs_pw=''

def depend_server_check():
    while True:
        if check_rs_ready() != True:
            Log.info('\tRS not ready')
            time.sleep(10)
            continue

        break


def check_rs_ready() -> bool:
    global rs_host
    global rs_port
    try:
        url = 'http://{}:{}/'.format(rs_host, rs_port)
        Log.debug('[check_rs_ready]\n\turl: {}'.format(url))
        resp = requests.get(url=url)
    except: return False
    Log.print_response(resp)
    if resp.status_code != 200: return False
    return True

def get_access_token():
    global rs_host
    global rs_port
    global rs_uname
    global rs_pw
    url = 'http://{}:{}/elapi/login?username={}&password={}'.format(rs_host, rs_port, rs_uname, rs_pw)
    Log.debug('[get_access_token]\n\turl: {}'.format(url))
    resp = requests.post(url=url)
    Log.print_response(resp)
    if resp.status_code != 200: return False, ''
    return True, resp.json()['access_token']


def res_upload(access_token):
    global rs_host
    global rs_port

    prop_file_path = './devs_all_properties/'
    for f in os.listdir(prop_file_path):
        if '.json' not in f: continue
        f_path = prop_file_path + f
        if not os.path.isfile(f_path): continue

        f_dev = open(f_path, mode = 'r')
        dict_dev_props = json.load(f_dev)
        f_dev.close()

        try:
            dev_id = f.replace('.json', '') + str(time.time()).replace('.', '')
            req_url =  "http://{}:{}/elapi/v1/devices/{}/properties/".format(rs_host, rs_port, dev_id)
            response = requests.post(
                headers = {
                    'Content-Type': 'application/json', 
                    'Access-Token': access_token
                    },
                url = req_url,
                json =  dict_dev_props
            )
            if response.status_code == 200:
                print(req_url)
            else:
                print('!!faild', req_url, response.status_code, response.text)

        except Exception as ex:
            print(type(ex).__name__, ex.args)

        time.sleep(0.05)


def main(args: list):
    global rs_host
    global rs_port
    global rs_uname
    global rs_pw

    Log.info('parameter:\n\tfhir_rs_host:{}\n\tfhir_rs_port:{}\n\tfhir_uname:{}\n\tfhir_pw:{}'.format(
        args[1], args[2], args[3], args[4]
    ))

    rs_host = args[1]
    rs_port = args[2]
    rs_uname = args[3]
    rs_pw = args[4]

    depend_server_check()
    result, access_token = get_access_token()
    if result != True:
        Log.error('access token get error')
        return
    
    res_upload(access_token)


if __name__ == '__main__':
    main(sys.argv)