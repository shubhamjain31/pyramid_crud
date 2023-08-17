from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from functools import wraps

from core.utils import decodeJWT
from core.database import models

def login_required(wrapped):
    def wrapper(request, *args, **kw):
        user = request.authenticated_userid
        
        if user is None:
            url = request.route_url('login') 
            return HTTPFound(location=url)
        else:
            return wrapped(request, *args, **kw)
    return wrapper

def is_authenticate(wrapped):
    def wrapper(request, *args, **kw):
        user_session = bool(request.session)

        if user_session is False:
            url = request.route_url('logout') 
            return HTTPFound(location=url)
        else:
            return wrapped(request, *args, **kw)
    return wrapper

def token_required(wrapped):
    @wraps(wrapped)
    def wrapper(request, *args, **kwargs):

        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # return 401 if token is not passed
        if not token:
            return Response(json_body={'status': 401, 'message': 'Token is missing !!!', 'data': {}}, 
                                status=401, content_type='applications/json')
  
        try:
            # decoding the payload to fetch the stored details
            algorithm = request.registry.settings['core.algorithm']
            secret    = request.registry.settings['core.secret']

            data = decodeJWT(token, algorithm, secret)
            current_user = request.dbsession.query(models.User).filter_by(email = data['email']).first()

            if current_user is None:
                return Response(json_body={'status': 401, 'message': 'Invalid Authentication token!', 'data': {}}, 
                                status=401, content_type='applications/json')

        except Exception as e:
            return Response(json_body={'status': 401, 'message': 'Token is invalid !!', 'data': {}}, 
                                status=401, content_type='applications/json')
        # returns the current logged in users context to the routes
        return  wrapped(request, current_user, token, *args, **kwargs)
    return wrapper