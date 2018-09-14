from django.db import models;
from gllaunch.models import *
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

scoreWeights = [0.1, 0.15, 0.25, 0.50]

#holds the state of the game.  Retrieved by the client code when the
#game starts.
class CAState(models.Model):
    
    iSession = models.ForeignKey(InteractiveSession)
    currentLevel = models.SmallIntegerField(default=1)
    
    l1Score = models.FloatField(default=0)
    l1Completed = models.DateTimeField(default=None, null=True, blank=True)
    l2Score = models.FloatField(default=0)
    l2Completed = models.DateTimeField(default=None, null=True, blank=True)
    l3Score = models.FloatField(default=0)
    l3Completed = models.DateTimeField(default=None, null=True, blank=True)
    l4Score = models.FloatField(default=0)
    l4Completed = models.DateTimeField(default=None, null=True, blank=True)
    started = models.DateTimeField()
    completed = models.DateTimeField(default=None, null=True, blank=True)
    active = models.BooleanField(default=True)
    restarted = models.BooleanField(default=False)
    tool = models.CharField(max_length=4, default="none")
    surplusWood = models.SmallIntegerField(default=0)
    surplusFish = models.SmallIntegerField(default=0)

    def getBestScore(self):
        try:
            setting = getLevelSetting(self.iSession.resource_id).setting
        except:
            setting = 'all'
        bestScore = 0
        sessions = CAState.objects.filter(~Q(completed=None), active=False, iSession=self.iSession)
        for s in sessions:
            
            l1 = s.l1Score*scoreWeights[0]
            l2 = s.l2Score*scoreWeights[1]
            l3 = s.l3Score*scoreWeights[2]
            l4 = s.l4Score*scoreWeights[3]
            
            if setting == 'all':
                score = (l1 + l2 + l3 + l4)/100
            elif setting == '1to3':
                score = (l1 + l2 + l3)/50
            else:
                score = l4/50
            if score > bestScore:
                bestScore = score
        return bestScore

    def getBestState(self):
        try:
            setting = getLevelSetting(self.iSession.resource_id).setting
        except:
            setting = 'all'
        bestScore = 0
        bestState = None
        sessions = CAState.objects.filter(iSession=self.iSession)
        for s in sessions:
            
            l1 = s.l1Score*scoreWeights[0]
            l2 = s.l2Score*scoreWeights[1]
            l3 = s.l3Score*scoreWeights[2]
            l4 = s.l4Score*scoreWeights[3]
            
            if setting == 'all':
                score = (l1 + l2 + l3 + l4)/100
            elif setting == '1to3':
                score = (l1 + l2 + l3)/50
            else:
                score = l4/50
            if score >= bestScore:
                bestScore = score
                bestState = s
        return bestState
                                
    def totalScore(self):
        try:
            setting = getLevelSetting(self.iSession.resource_id).setting
        except:
            setting = 'all'
        l1 = self.l1Score*scoreWeights[0]
        l2 = self.l2Score*scoreWeights[1]
        l3 = self.l3Score*scoreWeights[2]
        l4 = self.l4Score*scoreWeights[3]
        
        if setting == 'all':
            score = (l1 + l2 + l3 + l4)/100
        elif setting == '1to3':
            score = (l1 + l2 + l3)/50
        else:
            score = l4/50
        return score
        
        
    @classmethod
    def getActiveState(cls, iSession):

        setting = getLevelSetting(iSession.resource_id)
        try:
            #get an existing game session
            state = CAState.objects.get(iSession=iSession, active=True)
            state.setting = setting
            return state
        except:
            try:
                if setting == 'only4':
                    level = 4
                else:
                    level = 1
            except:
                level = 1
            newGame = CAState(iSession=iSession)
            newGame.currentLevel = level
            newGame.iSession = iSession
            newGame.started = timezone.now()
            newGame.save()
            newGame.setting = setting
            return newGame

    
    @classmethod
    def restart(cls, iSession):
        
        setting = getLevelSetting(iSession.resource_id)
        with transaction.atomic():
            CAState.objects.filter(active=True, iSession=iSession).update(active=False, restarted=True)
            try:
                if setting == 'only4':
                    level = 4
                else:
                    level = 1
            except:
                level = 1
            
            newGame = CAState(iSession=iSession)
            newGame.currentLevel = level
            newGame.iSession = iSession
            newGame.started = timezone.now()
            newGame.save()
            iSession.closed = timezone.now()
            return newGame        
        return None
    
    
    def isCompleted(self):
        setting = getLevelSetting(self.iSession.resource_id)
        first3Complete = self.l1Completed != None and self.l2Completed != None and self.l3Completed != None
        if setting == '1to3' and first3Complete:
            return True
        if setting == 'only4' and self.l4Completed != None:
            return True
        if setting == 'all' and first3Complete and self.l4Completed != None:
            return True
        return False
    
    
    #save the current level
    def saveCurrentLevel(self, data):

        score = float(data['score'])
        level = int(data['level'])
        if level == 1:
            self.l1Score = score
            self.l1Completed = timezone.now()
        elif level == 2:
            self.l2Score = score
            self.l2Completed = timezone.now()
        elif level == 3:
            self.l3Score = score
            self.l3Completed = timezone.now()
        elif level == 4:
            self.l4Score = score
            self.l4Completed = timezone.now()
            
        isCompleted = self.isCompleted()            
        if isCompleted:
            self.currentLevel = 5
        else:
            self.currentLevel += 1
        self.tool = data['tool']
        self.surplusFish = int(data['fish'])
        self.surplusWood = int(data['wood'])

        levelSetting = getLevelSetting(self.iSession.resource_id)
        active = CALevel.objects.get(parent=self, level=int(level), active=True)        
        with transaction.atomic():
            if isCompleted:
                self.completed = timezone.now()
                self.iSession.closed = timezone.now()
                self.iSession.completed - True
                self.iSession.save()
            self.save()
            active.score = score
            active.completed = True
            active.active = False
            active.closed = timezone.now()
            active.save()
            return True    
        return False

    
    #cancel the active session and
    def cancelCurrentLevel(self):

        CALevel.objects.filter(parent=self, level=self.currentLevel, active=True).update(closed=timezone.now(), active=False)
        
    
    def startLevel(self, level):
        
        if self.currentLevel == 5:
            return False;
        
        with transaction.atomic():
            
            try:
                levelObj = CALevel.objects.get(parent=self, level=level, active=True)
                levelObj.score = 0;
                levelObj.started = timezone.now()
                levelObj.save()
                addRestart(self.iSession, level)
            except:
                try:
                    levelObj = CALevel.objects.get(perent=self, level=level, completed=True)
                    levelObj.completed = False
                    levelObj.closed = None
                    levelObj.save()
                except:
                    CALevel.objects.filter(parent=self, level=level, active=True).update(active=False, closed=timezone.now())
                    self.currentLevel = level
                    self.save()
                    newLevel = CALevel()
                    newLevel.active = True
                    newLevel.parent = self
                    newLevel.started = timezone.now() 
                    newLevel.level = level
                    newLevel.save()
            return True
        return False


def addRestart(iSession, level):
    try:
        restart = CARestart.objects.get(parent=iSession, level=level)
        restart.restarts += 1
        restart.save()
    except:
        restart = CARestart(parent=iSession, level=level)
        restart.save()
    
    
def getLevelSetting(class_id):
    try:
        setting = LevelSetting.objects.get(class_id=class_id).setting
        return setting
    except:
        return 'all'


#created whenever a level is saved.  EAch SavedLevel is associated with
#a CAState    
class CALevel(models.Model):
    parent = models.ForeignKey(CAState)
    level = models.SmallIntegerField(default=1)
    score = models.SmallIntegerField(default=0)
    active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    started = models.DateTimeField()
    closed = models.DateTimeField(default=None, null=True)
    
    
class CARestart(models.Model):
    parent = models.ForeignKey(InteractiveSession)
    restarts = models.SmallIntegerField(default=1)
    level = models.SmallIntegerField()
    
    
class LevelSetting(models.Model):
    setting = models.CharField(max_length=10, default='all')
    class_id = models.CharField(max_length=220)
    
