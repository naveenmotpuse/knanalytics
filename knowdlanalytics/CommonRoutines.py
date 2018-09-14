'''
Created on Apr 27, 2017
updated on Oct 25, 2017
@author: anuja
'''
def GetFormattedName(NameInDB) :
    strret = "" 
    tlist = { "Spider": "XL (dev.econdip.pearsoncmg.com)",
             "Prod": "XL-Prod (econdip.pearsoncmg.com)",
            "monetary_policy": "Monetary Policy",
            "cpi_inflation": "CPI",
            "opp_cost": "Opportunity Cost",
            "intro": "Introduction",
            "level1": "Level 1",
            "level2":"Level 2",
            "level3":"Level 3",
            "level4": "Level 4",
            "level5": "Level 5" }
    try :
        strret = tlist[NameInDB]
    except KeyError:
        strret = NameInDB
         
    return strret

#Anu 25-oct-2017 for QLInteraction
def IsValidRequest(reqLocation) :
    if reqLocation.find("econdip.pearsoncmg.com") == -1 :
        return False
    else :
        return True
    
    
    



#end of file.

        
