from flask import Blueprint
from flask import abort
from flask import request

import KeycloakAccess

permission_api = Blueprint('permission_api', __name__)

@permission_api.route('/login', methods=['POST'], strict_slashes=False)
def access_token_get():
    if 'username' not in request.args or 'password' not in request.args:
        abort(400)
   
    resp = KeycloakAccess.get_user_token(
        request.args.get('username'), request.args.get('password'))

    return resp.json(),  resp.status_code



# @permission_api.route('/refresh', methods=['POST'], strict_slashes=False)
# def access_token_refresh():
#     if 'refresh_token' not in request.args:
#         abort(400)

#     result, resp = KeycloakAccess.refresh_access_token(request.args.get('refresh_token'))
#     if result != True:
#         abort(401)
#         # or 500?

#     return resp.json()


@permission_api.route('/logout', methods=['POST'], strict_slashes=False)
def logout():
    if 'refresh_token' not in request.args:
        abort(400)

    result = KeycloakAccess.user_logout(request.args['refresh_token'])

    if result != True:
        abort(500)

    return 'logout successed', 200