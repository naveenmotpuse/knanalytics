'''
Created on 19-July-2016

@author: naveen@knowdl.com
'''

import json
from django.http.response import HttpResponse
from econ.utils import CorsHttpDecorator
from econ.gdp.models import Fred_ContriesGDPData, Fred_ContriesPOPData, Fred_StatesGDPData, Fred_StatesPOPData, Fred_TotalPOPData     


FRED_DB_MAP = { 
               'countrygdp': Fred_ContriesGDPData, 
               'countrypop':Fred_ContriesPOPData,
               'stategdp':Fred_StatesGDPData,
               'statepop':Fred_StatesPOPData,
               'totalpop':Fred_TotalPOPData
               }


#http://dev.econdip.pearsoncmg.com/econservice/data/econ/gdp/pull_fred_data/?fred_tool_name=countrygdp&srid=GDP&freq=a    
def pullFredData(request):  
    try:
        fred_tool_name =  request.GET['fred_tool_name'] 
        freq = request.GET.get('freq', "all")
        srid = request.GET.get('srid', "all")
    except:
        return HttpResponse(status=400)   
    try:
        kwargs = {}    
        kwargs.update({'srid': srid})
        kwargs.update({'freq': freq})        
        
        model_class = FRED_DB_MAP[fred_tool_name]
        model_class.fetchFredData(**kwargs);
        
        return HttpResponse(status=200)   
    except:
        return HttpResponse(status=400)




#http://dev.econdip.pearsoncmg.com/econservice/data/econ/gdp/get_fred_data/?fred_tool_name=countrygdp
@CorsHttpDecorator
def getFredData(request):
    
    #FredUSRegConGasPrice.fetchFredData()
    #FredUSRegAllFormGasPrice.fetchFredData()
    #FredCrudeOilPrices.fetchFredData()
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
        
    try:
        fred_tool_name = request.GET['fred_tool_name']
        
    except:
        return HttpResponse(status=400)    
   
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    frequency = request.GET.get('frequency', "a")
    series_id = request.GET.get('series_id', "GDP")
    kwargs = {}
    if start_date:
        kwargs.update({'start_date': start_date})
    if end_date:
        kwargs.update({'end_date': end_date})
    
    kwargs.update({'frequency': frequency})
    kwargs.update({'series_id': series_id})
        
    model_class = FRED_DB_MAP[fred_tool_name]
    
    try:
        results = model_class.getFredData(**kwargs)        
    except:
        return HttpResponse(status=400)
    response = [[result[0].isoformat(), float(result[1])] for result in results]
    return HttpResponse(json.dumps(response),
                        status=200, content_type="application/json")





#end of file 




