from pyramid.view import notfound_view_config
from pyramid.response import Response

@notfound_view_config(renderer='json')
def notfound_view(request):
    return Response(json_body={'status': 404, 'message': 'Page Not Found!', 'data': {}}, 
                                status=404, content_type='applications/json')
  