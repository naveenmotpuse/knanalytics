'''
Created on 19-July-2016

@author: naveen@knowdl.com
'''
#import sys
import requests
from django.db import models
from datetime import datetime
import decimal

FRED_KEY = '1c3266c33784d3a4a4b7875a34ae2364'
FRED_BASE_URL = 'https://api.stlouisfed.org/fred/series/observations?api_key=%s&file_type=json&observation_start=1920-01-01' % FRED_KEY

from django.utils.deconstruct import deconstructible

@deconstructible
class FredOperations(object):

  
    @classmethod
    def fetchFredData(cls,srid='all',freq='all'):
        if freq == 'all' and srid=='all':           
            for frequency in cls.frequency_array:
                for series_id in cls.series_array:
                    try:                    
                        try: 
                            cls.fetchFredSeriesData(series_id, frequency)
                        except:
                            #myexep = sys.exc_info()[0]
                            #print("Unexpected error:", myexep) 
                            pass
                    except:
                        pass
                          
        elif freq == 'all' and srid != 'all':
            series_id = srid  
            for frequency in cls.frequency_array:                              
                try:                    
                    try: 
                        cls.fetchFredSeriesData(series_id, frequency)
                    except:                        
                        pass
                except:
                    pass
        
        elif freq != 'all' and srid == 'all': 
            frequency = freq           
            for series_id in cls.series_array:
                try:                    
                    try: 
                        cls.fetchFredSeriesData(series_id, frequency)
                    except:                        
                        pass
                except:
                    pass
        elif freq != 'all' and srid != 'all':
            series_id = srid
            frequency = freq
            try: 
                cls.fetchFredSeriesData(series_id, frequency)
            except:                        
                pass
    
    
    
                  
    
    
    @classmethod
    def fetchFredSeriesData(cls, series_id="", frequency=""):   
        if series_id !="" and frequency !="":                        
            url_base = FRED_BASE_URL + '&series_id=%s&frequency=%s' % (series_id, frequency)
            response = requests.get(url_base, stream=True)
            if response.json().get('observations'):
                cls.objects.filter(freq=frequency,seriesid=series_id).delete()
                object_list = [cls(observation_date=datetime.strptime(item.get('date'), "%Y-%m-%d"),
                                   observation_value=decimal.Decimal(item.get('value')),
                                   freq=frequency,
                                   seriesid=series_id,
                                   ) for item in response.json().get('observations') if item.get('value') != '.']
                
                cls.objects.bulk_create(object_list)
                
        
            
    


    @classmethod
    def getFredData(cls, start_date=None, end_date=None,series_id="", frequency=""):
        if not start_date:
            start_date = cls.default_start_date
        if not end_date:
            end_date = datetime.today().strftime("%Y-%m-%d")
        return cls.objects.values_list('observation_date',
                                       'observation_value').filter(observation_date__range=[start_date, end_date],freq=frequency,seriesid=series_id)


class Fred_ContriesGDPData(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=20, decimal_places=3)
    freq = models.CharField(max_length=50)
    seriesid = models.CharField(max_length=100)

    class Meta:
        unique_together = (('observation_date','observation_value','freq','seriesid'),)

    observation_type = "GDP Data for countries"
    #frequency = "m","q","sa","a"    
    units = "lin"
    default_start_date = "1920-01-01"
    frequency_array = ["q","a"]
    series_array = ['GDP','GDPC1','GDPDEF','A939RC0Q052SBEA','A939RX0Q048SBEA','GDPPOT',
                    
                    'MKTGDPAUA646NWDB','MKTGDPBRA646NWDB','MKTGDPCAA646NWDB','MKTGDPCNA646NWDB','MKTGDPFRA646NWDB',
                    'MKTGDPDEA646NWDB','MKTGDPINA646NWDB','MKTGDPIDA646NWDB','MKTGDPITA646NWDB','MKTGDPJPA646NWDB',
                    'MKTGDPMXA646NWDB','MKTGDPNLA646NWDB','MKTGDPRUA646NWDB','MKTGDPSAA646NWDB','MKTGDPKRA646NWDB',
                    'MKTGDPESA646NWDB','MKTGDPCHA646NWDB','MKTGDPTRA646NWDB','MKTGDPGBA646NWDB','MKTGDPUSA646NWDB',
                    'NYGDPMKTPCDWLD',
                    
                    'PCAGDPAUA646NWDB','PCAGDPBRA646NWDB','PCAGDPCAA646NWDB','PCAGDPCNA646NWDB','PCAGDPFRA646NWDB',
                    'PCAGDPDEA646NWDB','PCAGDPINA646NWDB','PCAGDPIDA646NWDB','PCAGDPITA646NWDB','PCAGDPJPA646NWDB',
                    'PCAGDPMXA646NWDB','PCAGDPNLA646NWDB','PCAGDPRUA646NWDB','PCAGDPSAA646NWDB','PCAGDPKRA646NWDB',
                    'PCAGDPESA646NWDB','PCAGDPCHA646NWDB','PCAGDPTRA646NWDB','PCAGDPGBA646NWDB','PCAGDPUSA646NWDB',
                    'PCAGDP1WA646NWDB',
                    
                    'NYGDPPCAPKDAUS','NYGDPPCAPKDBRA','NYGDPPCAPKDCAN','NYGDPPCAPKDCHN','NYGDPPCAPKDFRA',
                    'NYGDPPCAPKDDEU','NYGDPPCAPKDIND','NYGDPPCAPKDIDN','NYGDPPCAPKDITA','NYGDPPCAPKDJPN',
                    'NYGDPPCAPKDMEX','NYGDPPCAPKDNLD','NYGDPPCAPKDRUS','NYGDPPCAPKDSAU','NYGDPPCAPKDKOR',
                    'NYGDPPCAPKDESP','NYGDPPCAPKDCHE','NYGDPPCAPKDTUR','NYGDPPCAPKDUSA','NYGDPPCAPKDGBR',
                    'NYGDPPCAPKDWLD',
                    
                    'NAGIGP01AUA661S','BRAGDPDEFAISMEI','CANGDPDEFAISMEI','NAGIGP01CNA661S','FRAGDPDEFAISMEI',
                    'DEUGDPDEFAISMEI','INDGDPDEFAISMEI','IDNGDPDEFAISMEI','ITAGDPDEFAISMEI','JPNGDPDEFAISMEI',
                    'MEXGDPDEFAISMEI','NLDGDPDEFAISMEI','RUSGDPDEFAISMEI','KORGDPDEFAISMEI','ESPGDPDEFAISMEI',
                    'CHEGDPDEFAISMEI','TURGDPDEFAISMEI','GBRGDPDEFAISMEI','USAGDPDEFAISMEI']
    
    

class Fred_ContriesPOPData(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=20, decimal_places=3)
    freq = models.CharField(max_length=50)
    seriesid = models.CharField(max_length=100)

    class Meta:
        unique_together = (('observation_date','observation_value','freq','seriesid'),)

    observation_type = "population Data for countries"
    #frequency = "m","q","sa","a"    
    units = "lin"
    default_start_date = "1920-01-01"
    frequency_array = ["q","a"]
    series_array = ['POPTTLUSA148NRUG',
                    
                    'POPTOTAUA647NWDB','POPTOTBRA647NWDB','POPTOTCAA647NWDB','POPTOTCNA647NWDB',
                    'POPTOTFRA647NWDB','POPTOTDEA647NWDB','POPTOTINA647NWDB','POPTOTIDA647NWDB',
                    'POPTOTITA647NWDB','POPTOTJPA647NWDB','POPTOTMXA647NWDB','POPTOTNLA647NWDB',
                    'POPTOTRUA647NWDB','POPTOTSAA647NWDB','POPTOTKRA647NWDB','POPTOTESA647NWDB',
                    'POPTOTCHA647NWDB','POPTOTTRA647NWDB','POPTOTGBA647NWDB','POPTOTUSA647NWDB',
                    'POPTOT1WA647NWDB']


    
class Fred_StatesGDPData(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=20, decimal_places=3)
    freq = models.CharField(max_length=50)
    seriesid = models.CharField(max_length=100)

    class Meta:
        unique_together = (('observation_date','observation_value','freq','seriesid'),)

    observation_type = "GDP Data for states"
    #frequency = "m","q","sa","a"
    units = "lin"
    default_start_date = "1920-01-01"
    frequency_array = ["q","a"]
    series_array = ['ALNGSP','AKNGSP','AZNGSP','ARNGSP','CANGSP','CONGSP','CTNGSP','DENGSP','FLNGSP','GANGSP','HINGSP','IDNGSP','ILNGSP',
                    'INNGSP','IANGSP','KSNGSP','KYNGSP','LANGSP','MENGSP','MDNGSP','MANGSP','MINGSP','MNNGSP','MSNGSP','MONGSP','MTNGSP',
                    'NENGSP','NVNGSP','NHNGSP','NJNGSP','NMNGSP','NYNGSP','NCNGSP','NDNGSP','OHNGSP','OKNGSP','ORNGSP','PANGSP','RINGSP',
                    'SCNGSP','SDNGSP','TNNGSP','TXNGSP','UTNGSP','VTNGSP','VANGSP','WANGSP','WVNGSP','WINGSP','WYNGSP',
                    
                    'ALRGSP','AKRGSP','AZRGSP','ARRGSP','CARGSP','CORGSP','CTRGSP','DERGSP','FLRGSP','GARGSP','HIRGSP','IDRGSP','ILRGSP',
                    'INRGSP','IARGSP','KSRGSP','KYRGSP','LARGSP','MERGSP','MDRGSP','MARGSP','MIRGSP','MNRGSP','MSRGSP','MORGSP','MTRGSP',
                    'NERGSP','NVRGSP','NHRGSP','NJRGSP','NMRGSP','NYRGSP','NCRGSP','NDRGSP','OHRGSP','OKRGSP','ORRGSP','PARGSP','RIRGSP',
                    'SCRGSP','SDRGSP','TNRGSP','TXRGSP','UTRGSP','VTRGSP','VARGSP','WARGSP','WVRGSP','WIRGSP','WYRGSP',
                    
                    'ALPCPI','AKPCPI','AZPCPI','ARPCPI','CAPCPI','COPCPI','CTPCPI','DEPCPI','FLPCPI','GAPCPI','HIPCPI','IDPCPI','ILPCPI',
                    'INPCPI','IAPCPI','KSPCPI','KYPCPI','LAPCPI','MEPCPI','MDPCPI','MAPCPI','MIPCPI','MNPCPI','MSPCPI','MOPCPI','MTPCPI',
                    'NEPCPI','NVPCPI','NHPCPI','NJPCPI','NMPCPI','NYPCPI','NCPCPI','NDPCPI','OHPCPI','OKPCPI','ORPCPI','PAPCPI','RIPCPI',
                    'SCPCPI','SDPCPI','TNPCPI','TXPCPI','UTPCPI','VTPCPI','VAPCPI','WAPCPI','WVPCPI','WIPCPI','WYPCPI']
    
    

class Fred_StatesPOPData(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=20, decimal_places=3)
    freq = models.CharField(max_length=50)
    seriesid = models.CharField(max_length=100)

    class Meta:
        unique_together = (('observation_date','observation_value','freq','seriesid'),)

    observation_type = "Population Data for states"
    #frequency = "m","q","sa","a"
    units = "lin"
    default_start_date = "1920-01-01"
    frequency_array = ["q","a"]
    series_array = ['ALPOP','AKPOP','AZPOP','ARPOP','CAPOP','COPOP','CTPOP','DEPOP','FLPOP','GAPOP','HIPOP','IDPOP','ILPOP',
                    'INPOP','IAPOP','KSPOP','KYPOP','LAPOP','MEPOP','MDPOP','MAPOP','MIPOP','MNPOP','MSPOP','MOPOP','MTPOP',
                    'NEPOP','NVPOP','NHPOP','NJPOP','NMPOP','NYPOP','NCPOP','NDPOP','OHPOP','OKPOP','ORPOP','PAPOP','RIPOP',
                    'SCPOP','SDPOP','TNPOP','TXPOP','UTPOP','VTPOP','VAPOP','WAPOP','WVPOP','WIPOP','WYPOP']
    
    


class Fred_TotalPOPData(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=20, decimal_places=3)
    freq = models.CharField(max_length=50)
    seriesid = models.CharField(max_length=100)

    class Meta:
        unique_together = (('observation_date','observation_value','freq','seriesid'),)

    observation_type = "Total Population: All Ages including Armed Forces Overseas"
    #frequency = "m","q","sa","a"
    units = "lin"
    default_start_date = "1920-01-01"
    frequency_array = ["m","q","sa","a"]
    series_array = ['POP']
    
    
    
    
    
# end of file





