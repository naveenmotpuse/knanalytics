from econ.ue.models import *
import thread
import time
import logging
import random

logger = logging.getLogger('fred_ue')

runcount = 0

class FredStartup:

    __hasRun = False
    
    def __init__(self, database):
        self.randid = random.randint(0,10000)
        logger.info('%d __INIT__ %s %s' % (self.randid, FredStartup.__hasRun, runcount))
        # logger.info('__INIT__ disabled for now')
        # return
        if not FredStartup.__hasRun:
            FredStartup.__hasRun = True
            self.stateData = FredUnemploymentData();
            thread.start_new_thread(self.run, ());
        
    def run(self):
        global runcount
        checkDelay = 60*60 # test for an hourly frequency      *24    # check once a day to see if the data is stale
        updateDelay = 60*60*24*14 # only try to update the data once every two weeks
        while True:
            runcount += 1
            logger.info("%d beginning run %d..." % (self.randid, runcount))
            try:
                logger.info("%d checking for stale data..." % self.randid)
                time.sleep(random.random()) # prevent contentions...
                if self.stateData.dataIsStale(updateDelay):
                    logger.info("%d STALE: trying to fetch data..." % self.randid)
                    self.stateData.fetchUnemploymentData()
                    logger.info("%d Fetch completed" % self.randid)
                else:
                    logger.info("%d Skip this time; the data is not stale." % self.randid)
            except:
                logger.info('%d an unexpected top level error occurred' % self.randid)
            time.sleep(checkDelay)








#end of file



