from django.db import models
from django.db import transaction
from gllaunch.models import InteractiveSession
from django.utils import timezone
import json

DEFAULT_LEVEL_SETTINGS = {'intro': True,
                          'level1': True,
                          'level2': True,
                          'level3': True,
                          'level4': True,
                          'level5': True
                          }

class InteractiveState(models.Model):
    iSession = models.ForeignKey(InteractiveSession)
    currentLevel = models.SmallIntegerField(default=1)
    started = models.DateTimeField()
    completed = models.DateTimeField(default=None, null=True)
    restarted = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    customData = models.TextField(default='')
    levels = models.SmallIntegerField()
    activated_levels = models.TextField(default=None, null=True)

    @classmethod
    def getOrCreateActiveState(cls, iSession, levelCount=1, intro=False):
            launchParam = iSession.getLaunchParam()
            if launchParam['custom_mode'] in ['practice', 'preview']:
                newGame = InteractiveState(iSession=iSession)
                newGame.iSession = iSession
                newGame.started = timezone.now()
                newGame.levels = levelCount
                newGame.currentLevel = 0
                return newGame
            try:
                state = cls.objects.get(iSession=iSession, active=True)
                return state
            except:
                with transaction.commit_on_success():
                    newGame = cls(iSession=iSession)
                    newGame.iSession = iSession
                    newGame.started = timezone.now()
                    newGame.levels = levelCount
                    if intro:
                        newGame.currentLevel = 0
                    newGame.save()
                    return newGame

    @classmethod
    def getOrCreateInteractiveState(cls, iSession, activated_levels='', levelCount=1):
            launchParam = iSession.getLaunchParam()
            dumped_activated_levels = json.dumps(activated_levels)
            if launchParam['custom_mode'] in ['practice', 'preview']:
                newGame = cls(iSession=iSession)
                newGame.iSession = iSession
                newGame.started = timezone.now()
                newGame.levels = levelCount
                newGame.activated_levels = dumped_activated_levels
                newGame.currentLevel = activated_levels[0]
                return newGame
            try:
                state = cls.objects.get(iSession=iSession, active=True)
                return state
            except:
                with transaction.commit_on_success():
                    newGame = cls(iSession=iSession)
                    newGame.iSession = iSession
                    newGame.started = timezone.now()
                    newGame.levels = levelCount
                    newGame.activated_levels = dumped_activated_levels
                    newGame.currentLevel = activated_levels[0]
                    newGame.save()
                    return newGame

    @classmethod
    def restart(cls, iSession):
        launchParam = iSession.getLaunchParam()
        if launchParam['custom_mode'] != 'do':
            return False
        with transaction.commit_on_success():
            stateObj = cls.objects.get(iSession=iSession,
                                       active=True
                                       )
            if not stateObj.isComplete():
                return False
            cls.objects.filter(iSession=iSession,
                               active=True
                               ).update(restarted=True,
                                        active=False
                                        )
            newSession = cls(iSession=iSession,
                             levels=stateObj.levels,
                             activated_levels=stateObj.activated_levels,
                             started=timezone.now()
                             )
            newSession.save()
            return True
        return False

    def isComplete(self):
        completed = InteractiveLevel.objects.filter(parent=self,
                                                    completed=True).count()
        if completed >= self.levels:
            return True
        return False

    def saveLevel(self, level, score=0, data=''):
        bestScore = True
        launchParam = self.iSession.getLaunchParam()
        if launchParam['custom_mode'] != 'do':
            return None
        with transaction.commit_on_success():
            if True:
                op = self.getCurrentOp()
                if (op == 'level_redo'):
                    try:
                        topScore = InteractiveLevel.objects.filter(
                                                       parent=self,
                                                       active=False,
                                                       level=level
                                                       ).order_by('-score')[0]
                        if topScore.score >= score:
                            bestScore = False
                            newScore = topScore.score
                            newLevelData = topScore.levelData
                            InteractiveLevel.objects.filter(pk=topScore.pk
                                                            ).update(
                                                               score=score,
                                                               levelData=data
                                                               )
                            score = newScore
                            data = newLevelData
                    except:
                        pass
                    InteractiveLevel.objects.filter(parent=self,
                                                    level=level,
                                                    completed=True
                                                    ).update(completed=False,
                                                             restarted=True
                                                             )
                    InteractiveLevel.objects.filter(
                                                parent=self,
                                                level=level,
                                                active=True
                                                ).update(score=score,
                                                         levelData=data,
                                                         completed=True,
                                                         active=False,
                                                         closed=timezone.now()
                                                         )
                elif op == 'full_redo':
                    if level == self.levels:
                        # saving the last level so run a score check
                        highScore = self.getHighestPastSessionScore()
                        currentScores = self.getCurrentScores()
                        newScore = 0
                        for i in range(0, len(currentScores)):
                            newScore += currentScores[i]
                        newScore += score
                        if newScore > highScore:
                            InteractiveLevel.objects.filter(
                                                parent=self,
                                                level=level,
                                                active=True
                                                ).update(
                                                        score=score,
                                                        levelData=data,
                                                        completed=True,
                                                        active=False,
                                                        closed=timezone.now()
                                                        )
                        else:
                            InteractiveLevel.objects.filter(
                                                parent=self,
                                                level=level,
                                                active=True
                                                ).update(
                                                        score=score,
                                                        levelData=data,
                                                        completed=True,
                                                        active=False,
                                                        closed=timezone.now()
                                                        )
                            bestScore = False
                            s = self.getHighestScoringSession()
                            InteractiveState.objects.filter(pk=s.pk).update(
                                                                active=True,
                                                                restarted=False
                                                                )
                            self.active = False
                            self.restarted = True
                    else:
                        InteractiveLevel.objects.filter(
                                            parent=self,
                                            level=level,
                                            active=True
                                            ).update(score=score,
                                                     levelData=data,
                                                     completed=True,
                                                     active=False,
                                                     closed=timezone.now()
                                                     )
                else:
                    InteractiveLevel.objects.filter(
                                                parent=self,
                                                level=level,
                                                active=True
                                                ).update(
                                                     score=score,
                                                     levelData=data,
                                                     completed=True,
                                                     active=False,
                                                     closed=timezone.now()
                                                     )
                completed = self.isComplete()
                if self.activated_levels:
                    activated_levels = json.loads(self.activated_levels)
                    if completed:
                        self.currentLevel = -1
                    else:
                        try:
                            self.currentLevel = activated_levels[activated_levels.index(level) + 1]
                        except:
                            pass
                else:
                    if completed:
                        self.currentLevel = self.levels + 1
                    else:
                        self.currentLevel = level + 1
                if completed:
                    self.completed = timezone.now()
                self.save()
        return bestScore

    # cancel the active session and
    def cancelCurrentLevel(self):
        launchParam = self.iSession.getLaunchParam()
        if launchParam['custom_mode'] != 'do' or not self.isComplete():
            return
        self.currentLevel = self.levels+1
        self.save()
        InteractiveLevel.objects.filter(parent=self,
                                        level=self.currentLevel,
                                        active=True
                                        ).delete()

    def startLevel(self, level):
        launchParam = self.iSession.getLaunchParam()
        if launchParam['custom_mode'] != 'do':
            return False

        # don't start the new level if the
        history = self.getHistory()
        allowed = float(launchParam['custom_attemptsallowed'])
        if self.activated_levels:
            activated_levels = json.loads(self.activated_levels)
            if allowed != 0 and allowed <= history['attempts'][activated_levels.index(level)]:
                return False
        else:
            if allowed != 0 and allowed <= history['attempts'][level-1]:
                return False
        try:
            # check is an active level already exists, if so retrieve the
            # active level and reset the clock
            levelObj = InteractiveLevel.objects.get(parent=self,
                                                    level=level,
                                                    active=True
                                                    )
            levelObj.started = timezone.now()
            levelObj.save()
            # self.addLevelReload(level)
            return True
        except:
            # the level does not exist, so create a new one
            with transaction.commit_on_success():
                self.currentLevel = level
                self.save()
                newLevel = InteractiveLevel()
                newLevel.active = True
                newLevel.parent = self
                newLevel.started = timezone.now()
                newLevel.level = level
                newLevel.save()
                return True

    def addLevelReload(self, level):
        launchParam = self.iSession.getLaunchParam()
        if launchParam['custom_mode'] != 'do':
            return
        with transaction.commit_on_success():
            try:
                reload_object = InteractiveLevelReload.objects.get(parent=self,
                                                                   level=level
                                                                   )
                reload_object.reloads += 1
            except:
                reload_object = InteractiveLevelReload(parent=self,
                                                       level=level
                                                       )
            reload_object.save()
            self.currentLevel = level
            self.save()

    def restartLevel(self, level):
        launchParam = self.iSession.getLaunchParam()
        if launchParam['custom_mode'] != 'do':
            return
        if self.isComplete():
            with transaction.commit_on_success():
                InteractiveLevel.objects.filter(parent=self,
                                                level=level,
                                                completed=True
                                                ).update(restarted=True)
                levelObj = InteractiveLevel(parent=self,
                                            level=level,
                                            started=timezone.now()
                                            )
                levelObj.save()
                self.currentLevel = level
                self.save()

    def getHistory(self):
        history = {'attempts': [],
                   'highScore': -1
                   }
        try:
            highScore = HighScore.objects.get(iSession=self.iSession)
        except:
            initScores = []
            for _ in range(0, self.levels):
                initScores.append(-1)
            highScore = HighScore(iSession=self.iSession,
                                  scores=json.dumps({'scores': initScores})
                                  )
            highScore.save()
        history['highScore'] = highScore.scores
        attempts = history['attempts']
        for _ in range(0, self.levels):
            attempts.append(0)
        scores = InteractiveLevel.objects.filter(
                                             parent__iSession=self.iSession,
                                             active=False
                                             ).values('level',
                                                      'score'
                                                      ).order_by('level',
                                                                 '-score'
                                                                 )
        for s in scores:
            level = s['level']
            if self.activated_levels:
                activated_levels = json.loads(self.activated_levels)
                attempts[activated_levels.index(level)] += 1
            else:
                attempts[level-1] += 1
        history['attempts'] = attempts
        return history

    def getBestScore(self):
        states = InteractiveState.objects.filter(iSession=self.iSession,
                                                 active=False
                                                 )
        if len(states) == 0:
            return None
        highScore = 0
        highScoreComponents = []
        for _ in range(0, self.levels):
            highScoreComponents.append(0)
        for s in states:
            testScore = 0
            levelScores = []
            levels = InteractiveLevel.objects.filter(parent=s)
            for l in levels:
                testScore += l.score
                levelScores.append(l.score)
            if testScore > highScore:
                highScore = testScore
                highScoreComponents = levelScores
        return {'total': highScore,
                'levels': highScoreComponents,
                'state': s
                }

    def getScore(self):
        levels = InteractiveLevel.objects.filter(parent=self)
        totalScore = 0
        scoreComponents = []
        for l in levels:
            totalScore += l.score
            scoreComponents.append(l.score)
        return {'total': totalScore,
                'levels': scoreComponents
                }

    def getCurrentScores(self):
        scores = []
        completed = InteractiveLevel.objects.filter(parent=self,
                                                    completed=True)
        for i in range(0, len(completed)):
            scores.append(completed[i].score)
        return scores

    @classmethod
    def getSessionScores(cls, session):
        scores = []
        completed = InteractiveLevel.objects.filter(parent=session,
                                                    completed=True)
        for i in range(0, len(completed)):
            scores.append(completed[i].score)
        return scores

    def getHighestPastSessionScore(self):
        states = InteractiveState.objects.filter(iSession=self.iSession,
                                                 active=False)
        if len(states) == 0:
            return 0
        highScore = 0
        for s in states:
            levels = InteractiveLevel.objects.filter(parent=s, completed=True)
            testScore = 0
            for i in range(0, len(levels)):
                testScore += levels[i].score
            if testScore > highScore:
                highScore = testScore
        return highScore

    def getHighestScoringSession(self):
        states = InteractiveState.objects.filter(iSession=self.iSession,
                                                 active=False)
        if len(states) == 0:
            return 0
        highScore = 0
        highSession = None
        for s in states:
            levels = InteractiveLevel.objects.filter(parent=s, completed=True)
            testScore = 0
            for i in range(0, len(levels)):
                testScore += levels[i].score
            if testScore > highScore:
                highScore = testScore
                highSession = s
        return highSession

    def getCurrentOp(self):
        states = InteractiveState.objects.filter(
                                    iSession=self.iSession).count()
        levels = InteractiveLevel.objects.filter(parent=self).count()
        if (levels > self.levels):
            return 'level_redo'
        if (states > 1):
            return 'full_redo'
        return 'first_try'

    def getHighScores(self):
        try:
            hScores = HighScore.objects.filter(iSession=self.iSession)
            hScores = json.loads(hScores[0].scores)
            return hScores['scores']
        except:
            hScores = []
            for _ in range(self.levels):
                hScores.append(-1)
        return hScores

    def saveNewHighScore(self, scores):
        scores = json.dumps({'scores': scores})
        HighScore.objects.filter(iSession=self.iSession).update(scores=scores)

    @classmethod
    def getAllAggregates(cls, iSession, levelcount=4):
        students = {}
        aggs = [{'score': 0, 'duration': 0, 'count': 0, 'levelScore': 0} for _ in range(levelcount)]
        results = InteractiveLevel.objects.filter(
                          parent__iSession__resource_id=iSession.resource_id,
                          parent__iSession__target_app=iSession.target_app,
                          active=False
                          )
        for r in results:
            params = r.parent.iSession.getLaunchParam()
            if 'Learner' in params['roles']:
                try:
                    levelScore = json.loads(r.levelData)['levelScore']
                except KeyError:
                    levelScore = 0
                duration = (r.closed - r.started).seconds
                try:
                    sScores = students[r.parent.iSession.user_id]
                except KeyError:
                    sScores = {}
                try:
                    currentScore = sScores[str(r.level)]
                    if r.score > currentScore[0]:
                        sScores[str(r.level)] = (r.score, duration, levelScore)
                        students[r.parent.iSession.user_id] = sScores
                except:
                    sScores[str(r.level)] = (r.score, duration, levelScore)
                    students[r.parent.iSession.user_id] = sScores
                params = r.parent.iSession.getLaunchParam()
                aggs[r.level]['score'] += r.score
                aggs[r.level]['score'] = round(aggs[r.level]['score'], 2)
                aggs[r.level]['levelScore'] += levelScore
                aggs[r.level]['levelScore'] = round(aggs[r.level]['levelScore'], 2)
                aggs[r.level]['duration'] += float((r.closed - r.started).seconds) / 60
                aggs[r.level]['count'] += 1
        highScoreCount = [0 for _ in range(levelcount)]
        highScores = [{'score': 0, 'duration': 0, 'levelScore': 0} for _ in range(levelcount)]
        for s in students.values():
            for idx in range(0, levelcount):
                try:
                    highScores[idx]['score'] += s[str(idx)][0]
                    highScores[idx]['score'] = round(highScores[idx]['score'], 2)
                    highScores[idx]['duration'] += s[str(idx)][1]
                    highScores[idx]['levelScore'] += s[str(idx)][2]
                    highScores[idx]['levelScore'] = round(highScores[idx]['levelScore'], 2)
                    highScoreCount[idx] += 1
                except:
                    pass
        highScore = 0
        highDuration = 0
        if len(students) > 0:
#             for idx in range(levelcount-1, -1, -1):
#                 if highScores[idx]['duration'] == 0:
#                     del highScores[idx]
            for idx in range(0, len(highScores)):
                highScores[idx]['score'] = highScores[idx]['score']/float(len(students))
                highScores[idx]['score'] = round(highScores[idx]['score'], 2)
                highScores[idx]['duration'] = round(highScores[idx]['duration']/float(len(students)*60), 1)
                highScores[idx]['levelScore'] = highScores[idx]['levelScore']/float(len(students))
                highScores[idx]['levelScore'] = round(highScores[idx]['levelScore'], 2)
                highScore += highScores[idx]['score']
                highDuration += highScores[idx]['duration']
        avgDuration = 0
        avgScore = 0
#         for idx in range(levelcount-1, -1, -1):
#             if aggs[idx]['count'] == 0:
#                 del aggs[idx]
        for idx in range(0, len(aggs)):
            if aggs[idx]['count'] > 0:
                aggs[idx]['score'] = aggs[idx]['score']/(float(aggs[idx]['count']))
                aggs[idx]['duration'] = round(aggs[idx]['duration']/float(aggs[idx]['count']), 1)
                aggs[idx]['levelScore'] = aggs[idx]['levelScore']/float(aggs[idx]['count'])
                aggs[idx]['levelScore'] = aggs[idx]['levelScore']
                aggs[idx]['score'] = round(aggs[idx]['score'], 2)
                aggs[idx]['levelScore'] = round(aggs[idx]['levelScore'], 2)
                avgDuration += aggs[idx]['duration']
                avgScore += aggs[idx]['score']
        response = {
                    'levels': aggs,
                    'duration': round(avgDuration, 1),
                    'score': round(avgScore, 2),
                    'highscores': highScores,
                    'highScore': round(highScore, 2),
                    'highDuration': round(highDuration, 1),
                    }
        return response

    @classmethod
    def getStudentData(cls, iSession, user_id, levelcount=4):
        highScores = [{'score': 0,
                       'duration': 0,
                       'levelScore': 0
                       } for _ in range(levelcount)]
        results = InteractiveLevel.objects.filter(
                              parent__iSession__user_id=user_id,
                              parent__iSession__resource_id=iSession.resource_id,
                              parent__iSession__target_app=iSession.target_app,
                              active=False).order_by('started')
        for r in results:
            duration = (r.closed - r.started).seconds
            score = r.score
            levelScore = score
            try:
                levelScore = json.loads(r.levelData)['levelScore']
            except KeyError:
                levelScore = 0
            levelHighScore = highScores[r.level]
            if score > levelHighScore['score']:
                levelHighScore['score'] = float(score)
                levelHighScore['duration'] = float(duration)/60
                levelHighScore['levelScore'] = levelScore
        highScore = 0
        highDuration = 0
#         for idx in range(levelcount-1, -1, -1):
#             if highScores[idx]['duration'] == 0:
#                 del highScores[idx]
        for levelHighScore in highScores:
            highScore += levelHighScore['score']
            levelHighScore['duration'] = round(levelHighScore['duration'], 1)
            highDuration += levelHighScore['duration']
        highDuration = round(highDuration, 2)
        jsonData = cls.getResultAggregates(results, levelcount)
        jsonData['highScores'] = highScores
        jsonData['highScore'] = round(highScore, 2)
        jsonData['highDuration'] = round(highDuration, 1)
        return jsonData

    @classmethod
    def getResultAggregates(cls, results, levelcount):
        aggs = [{'score': 0,
                 'duration': 0,
                 'count': 0,
                 'levelScore': 0} for idx in range(levelcount)]
        for r in results:
            aggs[r.level]['score'] += r.score
            aggs[r.level]['duration'] += float((r.closed - r.started).seconds)/60
            aggs[r.level]['count'] += 1
            try:
                levelScore = json.loads(r.levelData)['levelScore']
            except KeyError:
                levelScore = 0
            aggs[r.level]['levelScore'] += levelScore
        avgDuration = 0
        avgScore = 0
#         for idx in range(levelcount-1, -1, -1):
#             if aggs[idx]['count'] == 0:
#                 del aggs[idx]
        for idx in range(0, len(aggs)):
            count = aggs[idx]['count']
            if count > 0:
                aggs[idx]['score'] = aggs[idx]['score']/(float(aggs[idx]['count'])*100)
                aggs[idx]['duration'] = round(aggs[idx]['duration']/float(aggs[idx]['count']), 1)
                aggs[idx]['levelScore'] = aggs[idx]['levelScore']/float(aggs[idx]['count'])
                aggs[idx]['levelScore'] = round(aggs[idx]['levelScore'], 2)
                avgDuration += round(aggs[idx]['duration'], 2)
                avgScore += aggs[idx]['score']
        resultData = {'levels': aggs,
                      'score': round(avgScore*100, 2),
                      'duration': round(avgDuration, 1),
                      }
        return resultData


class InteractiveLevel(models.Model):
    parent = models.ForeignKey(InteractiveState)
    level = models.SmallIntegerField(default=1)
    score = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    restarted = models.BooleanField(default=False)
    started = models.DateTimeField()
    closed = models.DateTimeField(default=None, null=True)
    levelData = models.TextField(default='')


class InteractiveLevelReload(models.Model):
    parent = models.ForeignKey(InteractiveState)
    reloads = models.SmallIntegerField(default=1)
    level = models.SmallIntegerField()


class InteractiveHighScore(models.Model):
    iSession = models.ForeignKey(InteractiveSession)
    highScore = models.SmallIntegerField(default=-1)


class HighScore(models.Model):
    iSession = models.ForeignKey(InteractiveSession)
    scores = models.TextField()

class InteractiveSettings(models.Model):
    settings = models.TextField(default=json.dumps(DEFAULT_LEVEL_SETTINGS))
    class_id = models.CharField(max_length=220)

    @classmethod
    def getOrCreateSettings(cls, class_id):
        try:
            return cls.objects.get(class_id=class_id)
        except:
            return cls.objects.create(class_id=class_id)