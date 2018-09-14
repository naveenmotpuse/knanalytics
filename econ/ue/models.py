from django.db import models
from gllaunch.models import *
from econ.ue import stateTables
import requests
import StringIO
import re
import thread
import json
import logging
import datetime
import time
import datetime

logger = logging.getLogger('fred_ue')

class UESettings(models.Model):
    settings = models.TextField(default=json.dumps({'levels':'all', 'useNaturalRate':True}))
    class_id = models.CharField(max_length=220)
    
class FredUnemploymentData(models.Model):
    state = models.CharField(max_length=10, db_index=True)
    data = models.TextField()
    urlBase = 'http://research.stlouisfed.org/fred2/data/'

    def dataIsStale(self, updateSeconds):
        lastUpdate = 0
        statusRecord = None
        try:
            statusRecord = FredUnemploymentData.objects.get(state="STATUS")            
            status = json.loads(statusRecord.data)
        except FredUnemploymentData.DoesNotExist:
            status = {'lastUpdate': 0.0}
            statusRecord = FredUnemploymentData(state="STATUS", data=json.dumps(status))

        curEpochTime = time.mktime(datetime.datetime.now().timetuple())

        logger.info('staleness check: curEpoch(%d) - lastUpdate(%d) = %d' % (curEpochTime, status['lastUpdate'], curEpochTime - status['lastUpdate']) )
        if curEpochTime > status['lastUpdate'] + updateSeconds:
            statusRecord.data = json.dumps({'lastUpdate': curEpochTime})
            statusRecord.save()
            return True
        else:
            return False



    def fetchDataSet(self, table, startDate=None, timeout=None):
        searchRE = re.compile('\d{4}-\d{2}-\d{2}')        
        fetchUrl = self.urlBase + table + '.txt'
        logger.info("Fetching '"+fetchUrl+"'")
        if timeout == None:
            request = requests.get(fetchUrl)
        else:
            request = requests.get(fetchUrl, timeout=10.0)     
        dataBuffer = StringIO.StringIO(request.text)
        values = []
        startRecording = False
        lastValue = 0
        for l in dataBuffer:   
            words = l.split()    
            if len(words) == 0:
                continue
            theMatch = re.match(searchRE, words[0])
            if theMatch != None: #starts with a data, this is a data item
                if startDate == None:
                    startRecording = True
                    startDate = words[0]
                elif words[0] == startDate:
                    startRecording = True
                if startRecording:
                    try:
                        lastValue = float(words[1])
                        values.append(lastValue)
                    except:
                        values.append(lastValue)
        return {'start_date':startDate, 'values':values,}


    def fetchStateUnemploymentData(self, state):
        logger.info('process state data : %s' % state)
        print 'process state data : %s' % state
        start = timezone.now()
        s = stateTables.data[state]
        try:
            tableData = self.fetchDataSet(s['table'], '2000-01-01', timeout=10.0)
            stateData = {
                         'region':{
                                'values':tableData['values'], 
                                'name':s['name'], 
                                'id':state,
                            },
                          'start_date':tableData['start_date'],
                          'sub_regions':[]
                         }
            subRegions = s['sub_regions']
            for idx in range(0, len(subRegions)):
                #print 'parse regional table ' + subRegions[idx]['table']
                regionData = self.fetchDataSet(subRegions[idx]['table'], '2000-01-01', timeout=10.0)
                stateData['sub_regions'].append({'values':regionData['values'], 'name':subRegions[idx]['name'], 'id':subRegions[idx]['id']})
            try:
                dbEntry = FredUnemploymentData.objects.get(state=state)
                dbEntry.data = json.dumps(stateData)
            except FredUnemploymentData.DoesNotExist:
                dbEntry = FredUnemploymentData(state=state, data=json.dumps(stateData))
            dbEntry.save()
            end = timezone.now()
        except requests.Timeout:
            print 'fetch table for ' + state + ' has timed out'

    
    def fetchUnemploymentData(self):
        logger.info('fetch unemployment data')
        
        nationals = ['UNRATE', 'CIVPART', 'NROU']
        
        for idx in range(0, len(nationals)):
            tableData = self.fetchDataSet(nationals[idx])
            try:
                dbEntry = FredUnemploymentData.objects.get(state=nationals[idx])
                dbEntry.data = json.dumps(tableData)
            except:
                dbEntry = FredUnemploymentData(state=nationals[idx], data=json.dumps(tableData))
            dbEntry.save()



        try:
            tableData = self.fetchDataSet('UNRATE', '2000-01-01', timeout=10)
            usData = {
                      'region':{
                            'values':tableData['values'], 
                            'name':'United States',
                            'id':'US',
                        },
                        'start_date':tableData['start_date'], 
                        'sub_regions':[]
                      }

            for s in stateTables.data.items():
                tableData = self.fetchDataSet(s[1]['table'], '2000-01-01', timeout=10)
                subRegion = {
                    'values':tableData['values'],
                    'id':s[0],
                    'name':s[1]['name'],
                }
                usData['sub_regions'].append(subRegion)
            try:
                dbEntry = FredUnemploymentData.objects.get(state='US')
                dbEntry.data = json.dumps(usData)
            except:
                dbEntry = FredUnemploymentData(state='US', data=json.dumps(usData))
            dbEntry.save()
        except:
            pass

        for s in stateTables.data.items():
            # try:
            self.fetchStateUnemploymentData(s[0])
            #except:
            #    logger.error('an unexpected error occurred')
        logger.info('fetch unemployment data complete')

    def __unicode__(self):
        return self.state

def export_data_sets():
    data_dir = os.path.join(django.conf.settings.APP_ROOT, 'app/data/')
    usdata = {'NROU':'us_nairu_long.json', 'CIVPART':'us_labor_force.json', 'UNRATE': 'us_unemployment.json'}
    outname = ''
    for row in FredUnemploymentData.objects.all():
        if row.state in usdata:
            outname = usdata[row.state]
        else:
            outname = 'state_map_json/%s_urn.json' % row.state.upper()
        print row.state, outname
        with open(data_dir+outname, 'w') as f:
            f.write(row.data)
        
