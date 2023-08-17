def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/api/v1/')
    
    config.add_route('register', '/api/v1/account/register')
    config.add_route('login', '/api/v1/accounts/login')
    config.add_route('logout', '/api/v1/accounts/logout')
    
    config.add_route('addTrain', '/api/v1/add/train')
    config.add_route('allTrains', '/api/v1/trains/')
    config.add_route('specificTrain', '/api/v1/train/{id}')
    config.add_route('deleteTrain', '/api/v1/delete/train/{id}')
    
    config.add_route('book', '/api/v1/reservation/book')