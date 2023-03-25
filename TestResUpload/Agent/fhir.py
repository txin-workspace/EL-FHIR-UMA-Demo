import requests
from time import sleep
import Log
import sys

rs_host=''
rs_port=''
rs_uname=''
rs_pw=''

res_patient = {
    "resourceType": "Patient",
    "gender": "male",
    "birthDate": "2020-01-01",
    "active": True
}

res_obs_bodyT = {
    "resourceType": "Observation",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "subject": {
        "reference": ""
    },
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "8310-5",
                "display": "Body Temperature"
            }
        ]
    },
    "valueQuantity": {
        "value": 35.8,
        "unit": "C"
    }
}
res_obs_bodyW = {
    "resourceType": "Observation",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "subject": {
        "reference": ""
    },
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "29463-7",
                "display": "Body weight"
            }
        ]
    },
    "valueQuantity": {
        "value": 70,
        "unit": "kg"
    }
}
res_obs_bmi = {
    "resourceType": "Observation",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "subject": {
        "reference": ""
    },
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "39156-5",
                "display": "Body mass index"
            }
        ]
    },
    "valueQuantity": {
        "value": 80,
        "unit": "kg/m^2"
    }
}
res_obs_bloodP = {
    "resourceType": "Observation",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "subject": {
        "reference": ""
    },
    "component": [
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure"
                    }
                ]
            },
            "valueQuantity": {
                "value": 120,
                "unit": "mmHg"
            }
        },
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8462-4",
                        "display": "Diastolic blood pressure"
                    }
                ]
            },
            "valueQuantity": {
                "value": 80,
                "unit": "mmHg"
            }
        }
    ]
}
res_obs_heartR = {
    "resourceType": "Observation",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "subject": {
        "reference": ""
    },
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "8867-4",
                "display": "Heart rate"
            }
        ]
    },
    "valueQuantity": {
        "value": 70,
        "unit": "bpm"
    }
}
res_obs_pulseO = {
    "resourceType": "Observation",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }
            ]
        }
    ],
    "subject": {
        "reference": ""
    },
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "59408-5",
                "display": "Oxygen saturation in Arterial blood by Pulse oximetry"
            }
        ]
    },
    "valueQuantity": {
        "value": 99.8,
        "unit": "%"
    }
}


def depend_server_check():
    while True:
        if check_rs_ready() != True:
            Log.info('\tRS not ready')
            sleep(10)
            continue

        break


def check_rs_ready() -> bool:
    global rs_host
    global rs_port
    try:
        url = 'http://{}:{}/'.format(rs_host, rs_port)
        Log.debug('[check_rs_ready]\\n\turl: {}'.format(url))
        resp = requests.get(url=url)
    except: return False
    Log.print_response(resp)
    if resp.status_code != 200: return False
    return True


def upload_res_patinet(token, payload):
    global rs_host
    global rs_port
    url = 'http://{}:{}/fhir/Patient'.format(rs_host, rs_port)
    header = {
        'Accept-Charset': 'utf-8',
        'Content-Type': 'application/fhir+json; charset=UTF-8',
        'Access-Token': token
    }
    Log.debug('[upload_res_patinet]\n\turl: {}\n\theader: {}\n\tpayload: {}'.format(url, header, payload))
    resp = requests.post(url=url, headers=header, json=payload)
    if resp.status_code != 201: return False, ''
    return True, resp.json()['id']


def upload_res_obs(token, payload) -> bool:
    global rs_host
    global rs_port
    url = 'http://{}:{}/fhir/Observation'.format(rs_host, rs_port)
    header = {
        'Accept-Charset': 'utf-8',
        'Content-Type': 'application/fhir+json; charset=UTF-8',
        'Access-Token': token
    }
    Log.debug('[upload_res_obs]\n\turl: {}\n\theader: {}\n\tpayload: {}'.format(url, header, payload))
    resp = requests.post(url=url, headers=header, json=payload)
    if resp.status_code != 201: return False
    return True


def get_access_token():
    global rs_host
    global rs_port
    global rs_uname
    global rs_pw
    url = 'http://{}:{}/login'.format(rs_host, rs_port)
    payload = {'user_id': rs_uname,'user_password': rs_pw}
    Log.debug('[get_access_token]\n\turl: {}\n\tpayload: {}'.format(url, payload))
    resp = requests.post(url=url, json=payload)
    Log.print_response(resp)
    if resp.status_code != 200: return False, ''
    return True, resp.json()['access_token']


def res_upload():
    global res_patient
    global res_obs_bmi
    global res_obs_bloodP
    global res_obs_bodyT
    global res_obs_bodyW
    global res_obs_heartR
    global res_obs_pulseO
    # login
    result, token = get_access_token()
    if result != True:
        Log.error('login error')
        return
    
    # upload patient get id
    result, p_id = upload_res_patinet(token, res_patient)
    if result != True: 
        Log.error('create patient error')
        return
    
    # change data patient id
    # upload observations
    for res in [res_obs_bmi, res_obs_bloodP, res_obs_bodyT, res_obs_bodyW, res_obs_heartR, res_obs_pulseO]:
        res['subject']['reference'] = 'Patient/{}'.format(p_id)
        result = upload_res_obs(token, res)
        if result != True: Log.error('upload obs errore')


def main(args: list):
    global rs_host
    global rs_port
    global rs_uname
    global rs_pw

    Log.debug(args)

    Log.info('parameter:\n\tfhir_rs_host:{}\n\tfhir_rs_port:{}\n\tfhir_uname:{}\n\tfhir_pw:{}'.format(
        args[1], args[2], args[3], args[4]
    ))

    rs_host = args[1]
    rs_port = args[2]
    rs_uname = args[3]
    rs_pw = args[4]

    depend_server_check()
    res_upload()


if __name__ == '__main__':
    main(sys.argv)