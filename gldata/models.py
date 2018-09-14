
import re
import json
from django.db import models
from datetime import datetime
from django.utils.timezone import utc
from gldata.grading import grade
import hashlib
from django.utils import timezone

class SessionData(models.Model):
    #from django.utils import timezone

    session_id = models.CharField(max_length=200, unique=True, db_index=True) 
                                        # this is the unique combination of the custom_resource_id and the user_id
    session_creation_date = models.DateTimeField(auto_now_add=True, editable=True)
    session_launch_date = models.DateTimeField(auto_now=True, editable=True)
    course_end_date = models.DateTimeField()
    launch_mode = models.CharField(max_length=16)
                                        # this is to prevent overwriting data unless the mode is 'do'
    
    launch_data = models.TextField(default="{}")    # contains the TPI Launch data for the most recent launch, as a JSON encoded dict
    
    problem_state_data = models.TextField(default="{}")  # contains the most recently saved student data, encoded as JSON
    
    def deconstruct(self):
        kwargs = {'prefix': self.prefix}
        if self.extension is not None:
            kwargs['extension'] = self.extension
        return 'import.path.to.PKUploader', (), kwargs
            
    @classmethod
    def constructSessionID(cls, launch_dict):
        def hashFns():
            yield lambda: launch_dict['custom_resultid']+'&'+launch_dict['user_id']
            yield lambda: launch_dict['custom_resource_id']+'&'+launch_dict['user_id']
            yield lambda: launch_dict['custom_target_' + launch_dict['custom_currentquestion']]

        for hash in hashFns():
            try:
                return hashlib.md5(hash()).hexdigest()
            except KeyError:
                continue


    @classmethod
    def getOrCreateSession(cls, launch_dict):
        session_id = SessionData.constructSessionID(launch_dict)
        
        k_identifier_val = launch_dict['custom_target_' + launch_dict['custom_currentquestion']]
        k_ident = launch_dict['custom_target_' + launch_dict['custom_currentquestion']]
        if (k_identifier_val == 'cpi_inflation' or k_identifier_val == 'monetary_policy' 
            or k_identifier_val == 'opp_cost' or k_identifier_val == 'unemp' or k_identifier_val == 'demand_supply' 
            or k_identifier_val == 'gdp' or k_identifier_val == 'elasticity' or  k_identifier_val == 'production_possibilities_frontier'
	    or k_identifier_val == 'gains_from_trade'
            or k_identifier_val.find('qualsims') != -1 or k_identifier_val.find('econ_blair') != -1):
            
            newsession_id = session_id + '_' + k_ident.replace('/','').replace('-','').replace(' ','')
                   
            try:
                oldsession = SessionData.objects.get(session_id=session_id)
                if oldsession.session_id == session_id:   
                    oldsession.session_id = newsession_id
                    oldsession.save()
                    session_id = newsession_id
            except:
                session_id = newsession_id
                pass
        
        try:
            session = SessionData.objects.get(session_id=session_id)
            session.launch_mode = launch_dict['custom_mode']
            session.launch_data = json.dumps(launch_dict)
            # clear problem state data on preview mode
            if session.launch_mode == 'preview':
                session.problem_state_data = '{}'
            session.save()
            return session
        except SessionData.DoesNotExist:
            return SessionData.createSession(launch_dict)
    
    @classmethod
    def createSession(cls, launch_dict):
        '''
        the launch_dict is the dict of key/value pairs POSTed to us by the TPI launch; some of which we need to keep around
        for use when sending outcomes.
        
        An IntegrityError will be thrown by django if session_id is not unique.
        '''
        session_id = SessionData.constructSessionID(launch_dict)
        k_identifier_val = launch_dict['custom_target_' + launch_dict['custom_currentquestion']]
        k_ident = launch_dict['custom_target_' + launch_dict['custom_currentquestion']]
        if (k_identifier_val == 'cpi_inflation' or k_identifier_val == 'monetary_policy' 
            or k_identifier_val == 'opp_cost' or k_identifier_val == 'unemp' or k_identifier_val == 'demand_supply' 
            or k_identifier_val == 'gdp' or k_identifier_val == 'elasticity' or  k_identifier_val == 'production_possibilities_frontier'
	    or k_identifier_val == 'gains_from_trade'
            or k_identifier_val.find('qualsims') != -1  or k_identifier_val.find('econ_blair') != -1) :        
            session_id = session_id + '_' + k_ident.replace('/','').replace('-','').replace(' ','')
            
        try:
            end_date = datetime.strptime(launch_dict['course_end_date'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)
        except:
            end_date = timezone.now()
            #Leap Year 29 Feb generate issue for below statement 
            #end_date = end_date.replace(year=end_date.year+1)
            try:                
                end_date = end_date.replace(year=end_date.year+1)
            except:
                end_date = end_date.replace(day=end_date.day-1).replace(year=end_date.year+1)
            
        encoded_dict = json.dumps(launch_dict)
        launch_type = launch_dict['custom_mode']
        session = SessionData.objects.create(session_id=session_id,
                                             launch_mode=launch_type,
                                             launch_data=encoded_dict,
                                             course_end_date=end_date)
        session.save()
        return session

    def problem_assignment_info(self, guid):
        'Returns problem number and total points'
        # turn launch_data into a python dictionary
        launch_dict = json.loads(self.launch_data)
        # find out which problem number matches the guid for this assignment
        for k, v in launch_dict.iteritems():
            m = re.match('custom_target_(\d+)', k)
            if not m:
                continue
            if v != guid:
                continue
            pnum = m.group(1)
            points = int(launch_dict['custom_points_' + pnum])
            return (pnum, points)
        return None

    def __unicode__(self):
        return self.session_id



class ProblemDefinition(models.Model):
    
    problem_guid = models.CharField(max_length=80, unique=True, db_index=True)
    problem_data = models.TextField(default='{}')   #structure defined by gl angular app; this is the problem setup
    correct_data = models.TextField(default='[]')   #array of structures defined by gl angular app; these are the correct journal entries

    def deconstruct(self):
        kwargs = {'prefix': self.prefix}
        if self.extension is not None:
            kwargs['extension'] = self.extension
        return 'import.path.to.PKUploader', (), kwargs
    
    def __unicode__(self):
        return self.problem_guid

    def grade_response(self, student_answers):
        '''
        returns a tuple of valid=True, JSON encoded results
        or a tuple of valid=False, some error message
        '''

        try:
            correct_answers = json.loads(self.correct_data)
            assert isinstance(student_answers, list)
        except ValueError:
            raise ValueError("correct_data is not valid JSON for problem_guid:"+self.problem_guid)
        except AssertionError:
            return ValueError("correct_data is not a list of objects for problem_guid:"+self.problem_guid)

        result = grade(student_answers, correct_answers)
        
        return result._asdict()
        
        
        





#end of file











