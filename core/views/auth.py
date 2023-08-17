from pyramid.response import Response
from pyramid.view import view_config

from core.database.security import check_password
from core.database import models
from core.schemas.model_schema import user_schema
from core.utils import decodeJWT
from core.decorators import token_required

from validators import is_invalid
import json, time

@view_config(route_name='login', request_method='POST', renderer='json', require_csrf=False)
def login(request):

    message_data = {}
    username = request.json_body.get("username", None)
    password = request.json_body.get("password", None)

    if username is None:
        return Response(json_body={'status': 400, 'message': 'Enter Username', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(username):
        return Response(json_body={'status': 400, 'message': 'Enter Username', 'data': {}}, 
                                status=400, content_type='applications/json')

    if password is None:
        return Response(json_body={'status': 400, 'message': 'Enter Password', 'data': {}}, 
                                    status=400, content_type='applications/json')
    
    if is_invalid(password):
        return Response(json_body={'status': 400, 'message': 'Enter Password', 'data': {}}, 
                                    status=400, content_type='applications/json')

    user = (
            request.dbsession.query(models.User)
            .filter_by(username=username)
            .first()
        )
    if user is not None and check_password(password, user.password):

        check_token = (
                            request.dbsession.query(models.Token)
                            .filter_by(email=user.email)
                            .first()
                        )

        if check_token is not None:
            # check if token is expired or not
            try:
                algorithm = request.registry.settings['core.algorithm']
                secret    = request.registry.settings['core.secret']

                payload = decodeJWT(check_token.token, algorithm, secret)
            except Exception as e:
                payload = None

            # if token is expired then delete token object
            if payload is None:
                request.dbsession.query(models.Token).filter_by(token=check_token.token).delete()
            else:
                data = {
                        "token": check_token.token
                    }
                return Response(json_body={'status': 200, 'message': 'Access Token!', 'data': data}, 
                                    status=200, content_type='applications/json')

        token_ = request.create_jwt_token(
                                        user.user_id,
                                        role=user.role,
                                        email=user.email,
                                        expires=time.time() + 3600       # expire in one hour
                                        )

        # create user token
        new_token = models.Token(email=user.email, token=token_, user_id=user.user_id)

        request.dbsession.add(new_token)

        data = {
            "token": new_token.token
        }
        return Response(json_body={'status': 200, 'message': 'Access Token!', 'data': data}, 
                                    status=200, content_type='applications/json')
    else:
        return Response(json_body={'status': 400, 'message': 'User not found!', 'data': {}}, 
                                    status=400, content_type='applications/json')

@view_config(route_name='register', request_method='POST', renderer='json', require_csrf=False)
def register(request):
    username    = request.json_body.get("username", None)
    password    = request.json_body.get("password", None)
    name        = request.json_body.get("name", None)
    email       = request.json_body.get("email", None)
    phone       = request.json_body.get("phone", None)
    role        = request.json_body.get("role", None)

    if username is None:
        return Response(json_body={'status': 400, 'message': 'Enter Username', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(username):
        return Response(json_body={'status': 400, 'message': 'Enter Username', 'data': {}}, 
                                status=400, content_type='applications/json')

    if password is None:
        return Response(json_body={'status': 400, 'message': 'Enter Password', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(password):
        return Response(json_body={'status': 400, 'message': 'Enter Password', 'data': {}}, 
                                status=400, content_type='applications/json')
    
    if name is None:
        return Response(json_body={'status': 400, 'message': 'Enter Name', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(name):
        return Response(json_body={'status': 400, 'message': 'Enter Name', 'data': {}}, 
                                status=400, content_type='applications/json')

    if email is None:
        return Response(json_body={'status': 400, 'message': 'Enter Email', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(email):
        return Response(json_body={'status': 400, 'message': 'Enter Email', 'data': {}}, 
                                status=400, content_type='applications/json')

    if phone is None:
        return Response(json_body={'status': 400, 'message': 'Enter Phone Number', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(phone):
        return Response(json_body={'status': 400, 'message': 'Enter Phone Number', 'data': {}}, 
                                status=400, content_type='applications/json')

    role = "admin" if is_invalid(role) else role

    user_query = request.dbsession.query(models.User).filter(models.User.email == email)
    user_obj = user_query.first()

    if user_obj:
        return Response(json_body={'status': 400, 'message': 'User already exists!', 'data': {}}, 
                                status=400, content_type='applications/json')

    new_user = models.User(username=username, password=password, name=name, email=email, phone=phone, is_active=True, 
                    ip_address=request.remote_addr, role=role)

    request.dbsession.add(new_user)

    return Response(json_body={'status': 201, 'message': 'User Created!', 'data': user_schema.dump(new_user)}, 
                                    status=201, content_type='applications/json')

@view_config(route_name='logout', request_method='GET', renderer='json', require_csrf=False)
@token_required
def logout(request, current_user, token):
    token_query = request.dbsession.query(models.Token).filter(models.Token.token == token)
    token_obj = token_query.one_or_none()

    if token_obj is not None:
        token_query.delete()
        return Response(json_body={'status': 200, 'message': 'User Logout Successfully!', 'data': {}}, 
                                    status=200, content_type='applications/json')
    else:
        return Response(json_body={'status': 400, 'message': 'Already Logout!', 'data': {}}, 
                                    status=400, content_type='applications/json')