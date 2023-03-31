import Log
import TokenKeeper
import HealthRsAccess
import KeycloakAccess
import HealthApi
import threading
import rs_config
from time import sleep


def start_agent():
    threading.Thread(target=job_polling_health_rs).start()



def job_polling_health_rs():
    while True:
        if TokenKeeper.health_rs_agent_token == None \
        or TokenKeeper.agent_token == None:
            sleep(10)
            continue

        try:
            Log.info('get health resource srver shared with me')
            update_health_rs_resource_info()
        except Exception as exc:
            Log.error('[update health rs resource info] {}'.format(exc))

        sleep(3)



# check 
# what resource not in el
#   register to rs, save info local
# what resource unshared
#   change local info or delete resource
def update_health_rs_resource_info():
    
    result, res_info_list = HealthRsAccess.get_sharewithme(
        TokenKeeper.health_rs_agent_token)

    if result != True:
        Log.error('[share_with_me_obtain] FIELD!!')
        raise Exception('Get health resource server shared with me field') 

    process_res_shared(res_info_list)
    process_res_unshared(res_info_list)
    process_patient_unshared(res_info_list)



def process_res_shared(sharedWithMe):
    # Log.warning('[process_res_shared]')
    # check
    #   new patient 
    #   patient prop shared change 
    for res_info in sharedWithMe:
        # Log.warning('[for loop - shared with me - item] {}'.format(res_info))

        if res_info['patient'] not in HealthApi.health_dict:
            # Log.warning('patient : {}'.format(res_info['patient']))
            # IF patient not exist
            # register res to am, and create location health care info
            result, res_id = KeycloakAccess.create_resource(
                '{}-{}-{}'.format('HealthRecorder', 'Patient', res_info['patient']),
                rs_config.agent_name_el
            )
            if result != True:
                raise Exception('Register health resource to el Keycloak server field') 

            # add res to dict
            HealthApi.health_dict[res_info['patient']] = HealthApi.Health()
            HealthApi.health_dict[res_info['patient']].patient_id = res_info['patient']
            HealthApi.health_dict[res_info['patient']].resource_id = res_id

            # Log.warning('{}'.format(HealthApi.health_dict))
            
        # check 
        # create new shared
        for share_id in res_info['proxy_share']:
            # Log.warning('[for loop - proxy_share - item] {}'.format(share_id))

            # Log.warning('{} - {}'.format(
                # share_id, 
                # str(HealthApi.health_dict[res_info['patient']].sub_res_list))
            # )
            if share_id in HealthApi.health_dict[res_info['patient']].sub_res_list:
                # Log.warning('in sub res list')
                continue

            result, policy_id = KeycloakAccess.share_resource_with_name(
                TokenKeeper.agent_token,
                HealthApi.health_dict[res_info['patient']].resource_id,
                res_info['proxy_share'][share_id]['target_type'],
                res_info['proxy_share'][share_id]['target'],
                "policy-{}-{}-{}-data_read".format(
                    share_id, 
                    res_info['proxy_share'][share_id]['target_type'], 
                    res_info['proxy_share'][share_id]['target'])
            )
            if result != True:
                # raise Exception('share health resource in el Keycloak server field')
                Log.error('[Agent] setting share field')
                continue
        
            # shared
            Log.warning('[for loop - proxy_share - item] shared!')

            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id] = HealthApi.SubFhirRes()
            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].fhir_id = res_info['hapi_id']
            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].fhir_type = res_info['hapi_type']
            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].shared_list.append(res_info['proxy_share'][share_id]['target'])
            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].health_rs_code = share_id
            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].el_rs_code = policy_id
            HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties = res_info['resource_type']
            if 'bloodPressure-s' in HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties and 'bloodPressure-d' in HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties:
                HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.remove('bloodPressure-s')
                HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.remove('bloodPressure-d')
                HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.append('bloodPressure')
            if 'birthDate' in HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties:
                HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.remove('birthDate')
                HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.append('age')
            # if 'identifier' in HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties:
                # HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.remove('identifier')
                # HealthApi.health_dict[res_info['patient']].sub_res_list[share_id].properties.append('id')

            # Log.warning('result -: {}'.format(HealthApi.health_dict[res_info['patient']].sub_res_list[share_id]))
    
    # Log.warning('[process_res_shared] Finish')



def process_res_unshared(sharedWithMe):
    # Log.warning('[process_res_unshared]')

    for p_id in HealthApi.health_dict:

        p_share_id_list = []
        for res_info in sharedWithMe:
            if p_id != res_info['patient']:
                continue
            
            p_share_id_list += res_info['proxy_share'].keys()

        unshared_list = []
        for share_id in HealthApi.health_dict[p_id].sub_res_list.keys():
            if share_id in p_share_id_list:
                continue

            # if fhir rs unshared ->
            # unshare in el am
            result, field_code = KeycloakAccess.unshare_resource(
                TokenKeeper.agent_token, 
                HealthApi.health_dict[p_id].sub_res_list[share_id].el_rs_code)

            if result != True:
                Log.error('[Agent] delete policy field! {} {} {}'.format(
                    HealthApi.health_dict[p_id].resource_id, 
                    HealthApi.health_dict[p_id].sub_res_list[share_id].el_rs_code, 
                    field_code))
                continue

            # del local info
            unshared_list.append(share_id)
            # HealthApi.health_dict[res_info['patient']].sub_res_list.pop(share_id)
            
        for unshared_id in unshared_list:
            if unshared_id in HealthApi.health_dict[p_id].sub_res_list:
                HealthApi.health_dict[p_id].sub_res_list.pop(unshared_id)

    # Log.warning('[process_res_unshared] Finish')



def process_patient_unshared(sharedWithMe):
    # Log.warning('[process_patient_unshared]')
    # check
    # patient deleted
    p_id_list = list(HealthApi.health_dict.keys())
    # Log.warning('[process_patient_unshared] p_id_list {}'.format(p_id_list))

    # Log.warning('health_dict {}'.format(HealthApi.health_dict))

    for p_id in p_id_list:
        for res_info in sharedWithMe:
            if p_id != res_info['patient']:
                # Log.warning('[process_patient_unshared] IN p_id_list')
                continue
            # if pid in health rs shared with me
            # remove from list
            if p_id == res_info['patient']:
                Log.warning('[process_patient_unshared] in list {}'.format(p_id))
                p_id_list.remove(p_id)
                break
    
    # Log.warning('[process_patient_unshared] p_id_list {}'.format(p_id_list))
    # in list = not in health rs shared with me -> patient unshared
    # if patient unshared -> delete am resource and chege local info
    for p_id in p_id_list:
        # delete in am
        result = KeycloakAccess.delete_resource(
            HealthApi.health_dict[p_id].resource_id)
        if result != True:
            Log.error('[Agent] delete resource field! {}'.format(
                HealthApi.health_dict[p_id].resource_id
            ))
            continue
        # delete local
        HealthApi.health_dict.pop(p_id)

    # Log.warning('[process_patient_unshared] Finish')
