from pyramid.view import view_config
from pyramid.renderers import render_to_response
from pyramid.response import Response

from core.database.models import User, Trains, Persons, Payments
from core.schemas.model_schema import train_schema, trains_schema

from datetime import datetime

from core.decorators import token_required
from core.tasks import add
from validators import is_invalid

from sqlalchemy import or_
from decouple import config

import razorpay, random

RAZORPAY_KEY_ID     = config("RAZORPAY_KEY_ID")
RAZORPAY_SECRET_KEY = config("RAZORPAY_SECRET_KEY")
PHONE_NUMBER        = config("PHONE_NUMBER")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET_KEY))

@view_config(route_name='home', request_method="GET", renderer='json')
def index(request):
    return Response(json_body={'status': 200, 'message': 'Welcome to RMS!', 'data': {}}, 
                                status=200, content_type='applications/json')

@view_config(route_name='addTrain', request_method="POST", renderer='json')
@token_required
def addTrain(request, current_user, token):
    train_number        = request.json_body.get("train_number", None)
    train_name          = request.json_body.get("train_name", None)
    source              = request.json_body.get("source", None)
    destination         = request.json_body.get("destination", None)
    time_               = request.json_body.get("time_", None)
    price               = request.json_body.get("price", None)
    seats_available     = request.json_body.get("seats_available", None)

    if train_number is None:
        return Response(json_body={'status': 400, 'message': 'Enter Train Number', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(train_number):
        return Response(json_body={'status': 400, 'message': 'Enter Train Number', 'data': {}}, 
                                status=400, content_type='applications/json')

    if train_name is None:
        return Response(json_body={'status': 400, 'message': 'Enter Train Name', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(train_name):
        return Response(json_body={'status': 400, 'message': 'Enter Train Name', 'data': {}}, 
                                status=400, content_type='applications/json')

    if source is None:
        return Response(json_body={'status': 400, 'message': 'Enter Source', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(source):
        return Response(json_body={'status': 400, 'message': 'Enter Source', 'data': {}}, 
                                status=400, content_type='applications/json')

    if destination is None:
        return Response(json_body={'status': 400, 'message': 'Enter Destination', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(destination):
        return Response(json_body={'status': 400, 'message': 'Enter Destination', 'data': {}}, 
                                status=400, content_type='applications/json')

    if time_ is None:
        return Response(json_body={'status': 400, 'message': 'Enter Time', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if is_invalid(time_):
        return Response(json_body={'status': 400, 'message': 'Enter Time', 'data': {}}, 
                                status=400, content_type='applications/json')

    if price is None:
        return Response(json_body={'status': 400, 'message': 'Enter Price', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if price == 0.0:
        return Response(json_body={'status': 400, 'message': 'Enter Price', 'data': {}}, 
                                status=400, content_type='applications/json')

    if seats_available is None:
        return Response(json_body={'status': 400, 'message': 'Enter Seats Availlable', 'data': {}}, 
                                    status=400, content_type='applications/json')

    if seats_available == 0:
        return Response(json_body={'status': 400, 'message': 'Enter Seats Available', 'data': {}}, 
                                status=400, content_type='applications/json')
    
    time_ = time_.split(":")
    str_time = f'{str(datetime.now().year)}-{str(datetime.now().month)}-{str(datetime.now().day)} {str(time_[0])}:{str(time_[1])}:00'
    train_time = datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
    
    new_train = Trains(train_number=train_number, train_name=train_name, source=source, time=train_time, destination=destination, price=price, 
                        seats_available=seats_available,
                    ip_address=request.remote_addr)
    request.dbsession.add(new_train)
    
    return Response(json_body={'status': 200, 'message': 'Train Added!', 'data': train_schema.dump(new_train)}, 
                                status=200, content_type='applications/json')

@view_config(route_name='allTrains', request_method="GET", renderer='json')
@token_required
def allTrains(request, current_user, token):
    slug = request.params.get("slug", None)
    
    if slug:
        all_trains = request.dbsession.query(Trains).filter(Trains.train_number == slug)
    else:
        all_trains = request.dbsession.query(Trains).all()
    
    return Response(json_body={'status': 200, 'message': 'All Train!', 'data': trains_schema.dump(all_trains)}, 
                                status=200, content_type='applications/json')

@view_config(route_name='specificTrain', request_method="GET", renderer='json')
@token_required
def specificTrain(request, current_user, token):
    id    = request.matchdict['id']

    train_obj = request.dbsession.query(Trains).filter_by(train_id=id).first()

    if train_obj is None:
        return Response(json_body={'status': 400, 'message': f'No Train with this id: {id} found', 'data': {}}, 
                                status=400, content_type='applications/json')
    
    return Response(json_body={'status': 200, 'message': 'Specific Train!', 'data': train_schema.dump(train_obj)}, 
                                status=200, content_type='applications/json')

@view_config(route_name='deleteTrain', request_method="DELETE", renderer='json')
@token_required
def deleteTrain(request, current_user, token):
    id    = request.matchdict['id']

    train_obj = request.dbsession.query(Trains).filter_by(train_id=id)

    if train_obj.first() is None:
        return Response(json_body={'status': 400, 'message': f'No Train with this id: {id} found', 'data': {}}, 
                                status=400, content_type='applications/json')
    
    train_obj.delete()
    return Response(json_body={'status': 200, 'message': 'Train Deleted!', 'data': {}}, 
                                status=200, content_type='applications/json')

temp = {}
@view_config(route_name='book', request_method="POST", renderer='json')  
@token_required
def book(request, current_user, token):
    global temp
    add.delay(1,2)
    source          = request.json_body.get("source", None)
    destination     = request.json_body.get("destination", None)
    name            = request.json_body.get("name", None)
    age             = request.json_body.get("age", None)
    gender          = request.json_body.get("gender", None)

    if current_user:
        trains = request.dbsession.query(Trains).filter_by(source=source.replace("_", " "), destination=destination.replace("_", " "))

        if trains.count():
            temp['name']        = name
            temp['age']         = age
            temp['gender']      = gender

            data = {'trains': trains_schema.dump(trains), 'key_id':RAZORPAY_KEY_ID ,'phone_number':PHONE_NUMBER}
            return Response(json_body={'status': 200, 'message': 'Available Trains!', 'data': data}, 
                                status=200, content_type='applications/json')
        else:
            return Response(json_body={'status': 400, 'message': 'No Available Trains!', 'data': {}}, 
                                status=400, content_type='applications/json')

    else:
        return Response(json_body={'status': 400, 'message': "Not a valid user. Please Login to continue", 'data': {}}, 
                                status=400, content_type='applications/json')