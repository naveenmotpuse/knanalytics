from django.http import HttpResponse

def set_access_control_headers(httpResponse, allowOrigin):
    httpResponse['Access-Control-Allow-Origin'] = allowOrigin
    httpResponse['Access-Control-Max-Age'] = '120'
    httpResponse['Access-Control-Allow-Credentials'] = 'true'
    httpResponse['Access-Control-Allow-Methods'] = 'HEAD,GET,OPTIONS,POST,DELETE'
    httpResponse['Access-Control-Allow-Headers'] = 'origin,content-type,accept,x-requested-with'
    return httpResponse

class CorsHttpDecorator(object):
    def __init__(self, f):
        self.f = f;
     
    def __call__(self, *args, **kwargs):
        request = args[0]
        try:
            httpOrigin = request.META['HTTP_ORIGIN']
        except KeyError:
            httpOrigin = "localhost"

        # print "CORS request origin host: '"+httpOrigin+"'"
        if 'localhost' in httpOrigin:
            allowOrigin = "*"
        else:
            allowOrigin = "*" # .pearsoncmg.com"

        if request.method == "OPTIONS": 
            response = HttpResponse()        
            set_access_control_headers(response, allowOrigin)        
            return response        
        else:
            response = self.f(*args, **kwargs)
            set_access_control_headers(response, allowOrigin)
            return response