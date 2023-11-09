from flask import abort
from flask import Blueprint
from flask import request

# import jwt
import json
import base64

import time

# import Health
import KeycloakAccess
import HealthRsAccess
import rs_config
import Log

health_api = Blueprint('health_api', __name__)

# resource index?
# patient_index? O
health_dict = {}

class Health:
    def __init__(self) -> None:
        self.patient_id = None# patient id
        self.resource_id = None# resource id in el_am
        # index health resource server policy id
        self.sub_res_list = {}

    def __str__(self):
        return str({
            'patient_id': self.patient_id,
            'resource_id': self.resource_id,
            'sub_res_list': self.sub_res_list
        })

    def __repr__(self):
        return str({
            'patient_id': self.patient_id,
            'resource_id': self.resource_id,
            'sub_res_list': self.sub_res_list
        })

class SubFhirRes:
    def __init__(self):
        self.fhir_id = None
        self.fhir_type = None
        self.properties = None
        self.shared_list = []
        self.agent_rpt = None
        self.agent_rpt_exp = None
        self.health_rs_code = None
        self.el_rs_code = None


    def check_shared(self, uname):
        if uname not in self.shared_list:
            return False
        return True

    def __str__(self):
        return str({
            'fhir_id': self.fhir_id,
            'fhir_type': self.fhir_type,
            'properties': self.properties,
            'shared_list': self.shared_list,
            'agent_rpt': self.agent_rpt,
            'agent_rpt_exp': self.agent_rpt_exp,
            'health_rs_code': self.health_rs_code,
            'el_rs_code': self.el_rs_code,
        })

    def __repr__(self):
        return str({
            'fhir_id': self.fhir_id,
            'fhir_type': self.fhir_type,
            'properties': self.properties,
            'shared_list': self.shared_list,
            'agent_rpt': self.agent_rpt,
            'agent_rpt_exp': self.agent_rpt_exp,
            'health_rs_code': self.health_rs_code,
            'el_rs_code': self.el_rs_code,
        })

# def fhir_el_converter(fhir_data: dict):
#     return

# def fhir_rs_access():
    # return

# def hr_resource_create():
    # return

# def fhir_desc_gen(hr_props: list):
#     for p_name in hr_props:
#         break
#     return

@health_api.errorhandler(401)
def not_found(error):
    return {"type": "referenceError", "message": "Token not allowed"}, 401


@health_api.errorhandler(404)
def not_found(error):
    return {"type": "referenceError", "message": "HTTP method or path is wrong"}, 404

# /
# healthCareRecord一覧

# /<healthCareRecordId>
# healthCareRecordのデータモデルを取得

# /<healthCareRecordId>/properties
# あるhealthCareRecordの詳細を取得

# /<healthCareRecordId>/properties/<propertyName>

@health_api.route('/', methods=['GET'], strict_slashes=False)
def get_all_info():
    
    hc_list = []
    # find all patient id
    # for patient_id in get_all_patient_id():
    if 'Access-Token' not in request.headers:
        for patient_id in health_dict:
            hc_list.append({
                'id': patient_id,
                'description': {
                    'ja': 'ユーザID:{}用'.format(patient_id),
                    'en': 'for user id {}'.format(patient_id),
                }
            })

    elif 'Access-Token' in request.headers:
        uname = get_uname_from_jwt(request.headers['Access-Token'])

        for patient_id in health_dict:
            for sub in health_dict[patient_id].sub_res_list:

                if health_dict[patient_id].sub_res_list[sub].check_shared(uname):
                    hc_list.append({
                        'id': patient_id,
                        'description': {
                            'ja': 'ユーザID:{}用'.format(patient_id),
                            'en': 'for user id {}'.format(patient_id),
                        }
                    })
                    break
                
    return {
        'healthCareRecorders': hc_list
    }

# def get_all_patient_id():
#     patient_list = set()
#     for res_id in health_dict:
#         patient_list.add(health_dict[res_id]['patient_id'])
#     return list(patient_list)



@health_api.route('/<healthCareRecordId>', methods=['GET'], strict_slashes=False)
def get_one_recorder_description(healthCareRecordId):

    if healthCareRecordId not in health_dict:
        abort(404)

    # no rpt return ticket
    if 'RPT' not in request.headers:
        return return_permisson_ticket(healthCareRecordId)

    # has rpt, check rpt, 
    # if not active return ticket, else check detail, 
    resule, rpt_detail = KeycloakAccess.check_rpt(request.headers['RPT'])

    if resule == False:
        Log.error('[check rpt] FAILED!!!')
        return return_permisson_ticket(healthCareRecordId)

    u_name = get_uname_from_jwt(request.headers['RPT'])

    # all pass, find device, and return
    # for p in rpt_detail['permission']:
    if 'data_read' not in rpt_detail['permissions'][0]['scopes']:
        return return_permisson_ticket(healthCareRecordId)

    if rpt_detail['permissions'][0]['resource_id'] != health_dict[healthCareRecordId].resource_id:
        return return_permisson_ticket(healthCareRecordId)

    props_desc = {
        "healthCareRecordType": "pcha",
        "descriptions": {
            "ja": "PCHA連携用ヘルスケアレコード",
            "en": "healthcare record for PCHA linkage"
        },
        "properties": {}
    }
    for fsid in health_dict[healthCareRecordId].sub_res_list:
        if health_dict[healthCareRecordId].sub_res_list[fsid].check_shared(u_name) != True:
            continue
        for p_name in health_dict[healthCareRecordId].sub_res_list[fsid].properties:
            props_desc['properties'][p_name] = pcha_data_desc['properties'][p_name]

    return props_desc


        
def get_uname_from_jwt(rpt):
    rpt_body = rpt.split('.')[1]
    rpt_body += '=' *(4 - len(rpt_body) % 4)
    return json.loads(base64.b64decode(rpt_body).decode())['preferred_username']



@health_api.route('/<healthCareRecordId>/properties', methods=['GET'], strict_slashes=False)
def get_one_recorder(healthCareRecordId):

    if healthCareRecordId not in health_dict:
        abort(404)

    # no rpt return ticket
    if 'RPT' not in request.headers:
        return return_permisson_ticket(healthCareRecordId)

    # has rpt, check rpt, 
    # if not active return ticket, else check detail, 
    resule, rpt_detail = KeycloakAccess.check_rpt(request.headers['RPT'])

    if resule == False:
        Log.error('[check rpt] FAILED!!!')
        return return_permisson_ticket(healthCareRecordId)

    u_name = get_uname_from_jwt(request.headers['RPT'])

    # all pass, find device, and return
    # for p in rpt_detail['permission']:
    if 'data_read' not in rpt_detail['permissions'][0]['scopes']:
        return return_permisson_ticket(healthCareRecordId)

    if rpt_detail['permissions'][0]['resource_id'] != health_dict[healthCareRecordId].resource_id:
        return return_permisson_ticket(healthCareRecordId)

    prop_dict = {}
    for fsid in health_dict[healthCareRecordId].sub_res_list:
        res_props = []
        if health_dict[healthCareRecordId].sub_res_list[fsid].check_shared(u_name) != True:
            continue
        
        for p_name in health_dict[healthCareRecordId].sub_res_list[fsid].properties:
            prop_dict[p_name] = None
            res_props.append(p_name)

        # thread counter TODO
        # TODO Run in other thread
        job_uma_get_resource(
            prop_dict, res_props, health_dict[healthCareRecordId].sub_res_list[fsid])

    # if thread conter == 0 TODO
    return prop_dict
    


def job_uma_get_resource(prop_dict, p_name_list, fhie_res_info):
    # check rpt exp time
    if fhie_res_info.agent_rpt_exp == None or int(time.time()) >= fhie_res_info.agent_rpt_exp:

        # get ticket 
        result, rpt_req_info = HealthRsAccess.get_resource_ticket_checked(
            fhie_res_info.fhir_type, fhie_res_info.fhir_id
        )
        if result != True:
            return 

        # get rpt 
        result, rpt_resp = HealthRsAccess.get_rpt(
            rpt_req_info['as_url'], rpt_req_info['ticket'], rpt_req_info['audience']
        )
        if result != True:
            return 
        fhie_res_info.agent_rpt = rpt_resp['access_token']
        fhie_res_info.agent_rpt_exp = int(time.time()) + rpt_resp['expires_in'] - 5

    # get resource
    result, value_dict = HealthRsAccess.get_resource_value(
        fhie_res_info.agent_rpt, fhie_res_info.fhir_type, 
        fhie_res_info.fhir_id, fhie_res_info.properties
    )
    if result != True:
        return 

    for p_name in value_dict:
        if p_name not in p_name_list: 
            continue
        
        prop_dict[p_name] = value_dict[p_name]


# @health_api.route('/<healthCareRecordId>/properties', methods=['POST'], strict_slashes=False)
# def create_recorder(healthCareRecordId):
#     return 0


@health_api.route('/<healthCareRecordId>/properties/<propertName>', methods=['GET'], strict_slashes=False)
def get_recorder_one_prop(healthCareRecordId, propertName):

    if healthCareRecordId not in health_dict:
        abort(404)

    # no rpt return ticket
    if 'RPT' not in request.headers:
        return return_permisson_ticket(healthCareRecordId)

    # has rpt, check rpt, 
    # if not active return ticket, else check detail, 
    resule, rpt_detail = KeycloakAccess.check_rpt(request.headers['RPT'])

    if resule == False:
        Log.error('[check rpt] FAILED!!!')
        return return_permisson_ticket(healthCareRecordId)

    u_name = get_uname_from_jwt(request.headers['RPT'])

    # all pass, find device, and return
    # for p in rpt_detail['permission']:
    if 'data_read' not in rpt_detail['permissions'][0]['scopes']:
        return return_permisson_ticket(healthCareRecordId)

    if rpt_detail['permissions'][0]['resource_id'] != health_dict[healthCareRecordId].resource_id:
        return return_permisson_ticket(healthCareRecordId)

    prop_dict = {}
    for fsid in health_dict[healthCareRecordId].sub_res_list:
        res_props = []

        if health_dict[healthCareRecordId].sub_res_list[fsid].check_shared(u_name) != True:
            continue

        if propertName not in health_dict[healthCareRecordId].sub_res_list[fsid].properties:
            continue
        
        res_props.append(propertName)

        # thread counter TODO
        # TODO Run in other thread
        job_uma_get_resource(
            prop_dict, res_props, health_dict[healthCareRecordId].sub_res_list[fsid])

        break

    # if thread conter == 0 TODO
    Log.warning('propertName: {} - {}'.format(prop_dict, propertName))
    if propertName not in prop_dict:
        abort(404)

    return prop_dict



def return_permisson_ticket(hr_id):
    resule, ticket = KeycloakAccess.make_ticket(health_dict[hr_id].resource_id)
    if resule == False:
        Log.error('[create ticket] FAILED!!!')
        abort(401)
    
    return {
        'as_url': '{}:{}/realms/{}/protocol/openid-connect/token'.format(
            rs_config.am_host, rs_config.am_port, rs_config.realm_name),
        'ticket': ticket,
        'audience': rs_config.client_id,
        'authz_type': 'uma2.0'
    }, 401


pcha_data_desc = {
    "healthCareRecordType": "pcha",
    "descriptions": {
        "ja": "PCHA連携用ヘルスケアレコード",
        "en": "healthcare record for PCHA linkage"
    },
    "properties": {
        "id": {
            "descriptions": {
                "ja": "patient ID",
                "en": "patient ID"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "string"
            }
        },
        "age": {
            "descriptions": {
                "ja": "年齢",
                "en": "age"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "number"
            }
        },
        "gender": {
            "descriptions": {
                "ja": "性別",
                "en": "gender"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "string",
                "enum": [
                    "male",
                    "female",
                    "other",
                    "unknown"
                ],
                "values": [
                    {
                        "value": "male",
                        "descriptions": { 
                            "ja": "男性",
                            "en": "male"
                        },
                    }, {
                        "value": "female", 
                        "descriptions": { 
                            "ja": "女性",
                            "en": "female"
                        },
                    }, {
                        "value": "other",
                        "descriptions": {
                            "ja": "その他",
                            "en": "other"
                        },
                    }, {
                        "value": "unknown", 
                        "descriptions": { 
                            "ja": "不明",
                            "en": "unknown"
                        }
                    }
                ]
            }
        },
        "active": {
            "descriptions": {
                "ja": "Patientレコードがアクティブ使用中",
                "en": "Patient record is in active use"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "boolean",
                "values": [
                    {
                        "value": True,
                        "descriptions": { 
                            "ja": "アクティブ",
                            "en": "active"
                        },
                    }, 
                    {
                        "value": False,
                        "descriptions": {
                            "ja": "非アクティブ",
                            "en": "inactive"
                        }
                    }
                ]                
            }
        },
        "bmi": {
            "descriptions": {
                "ja": "BMI値",
                "en": "BMI"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "number",
                "unit": "kg/m^2"
            }
        },
        "bodyTemperature": {
            "descriptions": {
                "ja": "体温",
                "en": "body temperature"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "number",
                "unit": "Celsius"
            }
        },
        "bodyWeight": {
            "descriptions": {
                "ja": "体重",
                "en": "body weight"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "number",
                "unit": "kg"
            }
        },
        "bloodPressure": {
            "descriptions": { 
                "ja": "血圧",
                "en": "blood pressure"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "array",
                "items": {
                    "type": "number",
                    "unit": "mmHg"
                },
                "minItems": 2,
                "maxItems": 2
            }
        },
        "heartRate": {
            "descriptions": {
                "ja": "心拍数",
                "en": "heart rate"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "number",
                "unit": "/min"
            }
        },
        "pulseOximetry": {
            "descriptions": {
                "ja": "パルスオキシメータ(経皮的酸素飽和度)値",
                "en": "Pulse Oximetry"
            },
            "writable": False,
            "observable": False,
            "schema": {
                "type": "number",
                "unit": "%"
            }
        }
    }
}
