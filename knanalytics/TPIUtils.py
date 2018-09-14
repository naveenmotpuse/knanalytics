'''
Created on Jun 12, 2013

@author: charlieb
'''

import datetime
import uuid
import cgi
import hmac
import binascii
import urllib
import hashlib
import requests
import json
from datacapture.models import InteractiveLevel
from string import Template
from django.db.models import Q
from gllaunch.models import TPI_Launch_Log
from django.conf import settings
import requests

# for testing; example TPI launch data...
TEST_TPI_PARAMS = {
    "custom_lastname": "Tester",
    "custom_course_id": "urn:udson:pearson.com/xl/devdb:course/138261_xlnoedx_devdb",
    "context_id": "urn:udson:pearson.com/xl/devdb:course/138261",
    "custom_originating_partner": "xl",
    "custom_mode": "do",
    "custom_savevalues": "1",
    "custom_assignmenttitle": "GLv2 Homework 1",
    "tool_consumer_instance_guid": "TPI",
    "oauth_signature": "8wA6MDjZI1L6pG12b/oSfaljlBg=",
    "custom_courseenddate": "2013-09-22T00:00:00Z",
    "lti_message_type": "basic-lti-launch-request",
    "custom_print": "1",
    "custom_totalpoints": "4",
    "user_id": "urn:udson:pearson.com/xl/devdb:user/35870",
    "custom_partnerId": "xlnoedx",
    "custom_resource_id": "urn:udson:pearson.com/xl/devdb:homework/1800620",
    "custom_tool_proxy_guid": "d5bfe447-e208-43b5-b2fb-d2a0e1c3b3ad",
    "custom_questiontitle_1": "glv2-question1 (dev)",
    "custom_currentquestion": "1",
    "custom_questiontitle_3": "glv2-question3 (dev)",
    "custom_questiontitle_2": "glv2-question2 (dev)",
    "custom_partialcredit": "1",
    "custom_institutionId": "devdb",
    "custom_resultid_role": "$resultidrole",
    "custom_resultid": "urn:udson:pearson.com/xl/devdb:partnerhomeworkresult/46549",
    "custom_displaycourseid": "02Y1OL501Y2QD0",
    "custom_person_id": "gl-instructor",
    "oauth_nonce": "9055125895952954184",
    "oauth_timestamp": "1372790318",
    "custom_points_3": "1",
    "custom_points_2": "1",
    "custom_points_1": "1",
    "oauth_signature_method": "HMAC-SHA1",
    "custom_points_4": "1",
    "oauth_version": "1.0",
    "custom_target_1": "GL0001",
    "resource_link_id": "UNKNOWN",
    "custom_target_3": "GL0003",
    "custom_target_2": "GL0002",
    "custom_target_4": "GL0004",
    "roles": "Educator",
    "context_type": "CourseSection",
    "lti_version": "LTI-1p0",
    "custom_membershipslastupdated": "2013-01-22T18:09:22.893Z",
    "custom_handler_urn": "pearson/xlnoedx_phgl2/slink/x-pearson-xlnoedx_phgl2",
    "custom_firstname": "GL",
    "custom_questiontitle_4": "glv2-question4 (dev)",
    "custom_attemptsallowed": "0",
    "oauth_consumer_key": "TPI",
    "custom_dateavailable": "2013-05-31T00:00:00Z"
}

TEST_EXTRA_PARAMS = {
    'transactionId': uuid.uuid4(),
    'dataSourceName': 'GL',
    'timeStamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
    'score': 1,
    'problem_guid': 'GL0001',
    'problemNumber': 1,
    'duration': 700,
    'submissionCount': 1
}

WRAPPER_TEMPLATE = '''
<tos:outcomeMessage xsi:schemaLocation="http://www.pearson.com/xsd/tpiOutcomesService_v1p0 tpiOutcomesService_v1p0.xsd" xsi:type="tos:OutcomeMessage.Type" xmlns:cor="http://www.imsglobal.org/services/lti/xsd/CoreOutcomesService_bv1p0" xmlns:tos="http://www.pearson.com/xsd/tpiOutcomesService_v1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <tos:messageInfo>
      <tos:dataSource>${custom_tool_proxy_guid}</tos:dataSource>
      <tos:dataSourceName>${dataSourceName}</tos:dataSourceName>
      <tos:transactionId>${transactionId}</tos:transactionId>
      <tos:timestamp>$timeStamp</tos:timestamp>
      <tos:partnerId>${custom_partnerId}</tos:partnerId>
      <tos:institutionId>${custom_institutionId}</tos:institutionId>
      <tos:contextIdentifier>$context_id</tos:contextIdentifier>
   </tos:messageInfo>
   $messageBody
</tos:outcomeMessage>
'''

REPLACE_RESULT_TEMPLATE = '''
   <cor:replaceResultRequest>
      <cor:sourcedId>${custom_resultid}</cor:sourcedId>
      <cor:resultRecord>
         <cor:sourcedId>${custom_resultid}</cor:sourcedId>
         <cor:result>
            <cor:statusofResult>
               <cor:handle>complete</cor:handle>
               <cor:displayName>complete</cor:displayName>
            </cor:statusofResult>
            <cor:personSourcedId>${user_id}</cor:personSourcedId>
            <cor:lineItemSourcedId>${custom_resource_id}</cor:lineItemSourcedId>
            <cor:date>${timeStamp}</cor:date>
            <cor:resultScore>
               <cor:language>en-US</cor:language>
               <cor:textString>${score}</cor:textString>
            </cor:resultScore>
            <cor:dataSource>${custom_tool_proxy_guid}</cor:dataSource>
            <cor:extension>
                <cor:extensionField>
                    <cor:fieldName>resultDetail</cor:fieldName>
                    <cor:fieldType>any</cor:fieldType>
                    <cor:fieldValue xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema">${extensionBody}</cor:fieldValue>
                </cor:extensionField>
                <cor:extensionField>
                    <cor:fieldName>messageDate</cor:fieldName>
                    <cor:fieldType>any</cor:fieldType>
                    <cor:fieldValue>$timeStamp</cor:fieldValue>
                </cor:extensionField>
            </cor:extension>
         </cor:result>
      </cor:resultRecord>
   </cor:replaceResultRequest>
'''

SIMPLE_ITEM_RESULT_TEMPLATE = '''
<?xml version="1.0" encoding="utf-16"?>
<resultDetails xmlns:psr="http://www.pearson.com/services/SimpleResults/data/v1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:psa="http://www.pearson.com/services/SimpleAssessment/data/v1p0" xmlns:tos="http://www.pearson.com/xsd/tpiOutcomesService_v1p0" xmlns:cor="http://www.imsglobal.org/services/lti/xsd/CoreOutcomesService_bv1p0">
    <psr:totalDuration></psr:totalDuration>
    <psr:parts>
        <psr:simpleSectionResult>
            <psr:parts>
              <psr:simpleItemResult>
                  <psr:itemBindingId>${problem_guid}</psr:itemBindingId>
                  <psr:itemId>${problemNumber}</psr:itemId>
                  <psr:itemScore>${score}</psr:itemScore>
                  <psr:duration>${duration}</psr:duration>
                  <psr:submissionCount>${submissionCount}</psr:submissionCount>
              </psr:simpleItemResult>
            </psr:parts>
        </psr:simpleSectionResult>
    </psr:parts>
</resultDetails>
'''
SIMPLE_ITEM_RESULT_TEMPLATE = ' '.join(SIMPLE_ITEM_RESULT_TEMPLATE.split())


def outcome_xml(params, **extra_params):
    params.update(extra_params)
    params['extensionBody'] = cgi.escape(Template(SIMPLE_ITEM_RESULT_TEMPLATE).substitute(params))
    params['messageBody'] = Template(REPLACE_RESULT_TEMPLATE).substitute(params)
    return Template(WRAPPER_TEMPLATE).substitute(params)


def oauth_sig(method, url, params, key=None):
    # If you dont have a token yet, the key should be only "CONSUMER_SECRET&"
    if key == None:
        key = settings.TPI_SHARED_SECRET + '&'
    else:
        key += '&'

    def quote(s):
        return urllib.quote(s, '')

    quotedParams = dict(params)
    print 'oauth_signature:', quotedParams.pop('oauth_signature')
    print 'params minus oauth_signature:', quotedParams

    quotedParams = sorted(quotedParams.iteritems(), key=lambda p: p[0])
    quotedParams = (quote(k) + '=' + quote(v) for (k, v) in quotedParams)
    quotedParams = quote('&'.join(quotedParams))

    quotedUrl = quote(url)

    raw = '&'.join([method, quotedUrl, quotedParams])
    msg = TPI_Launch_Log(message=raw)
    msg.save()
    
    print 'RAW: ', raw

    hashed = hmac.new(key, raw, hashlib.sha1)

    # The signature
    return binascii.b2a_base64(hashed.digest())[:-1]


def has_valid_signature(params, url=None, key=None):
    #refererurl = request.META['HTTP_REFERER']
    print 'vinodb referer--', key
    if url == '' or url == None:
        url = settings.LAUNCH_URL
    try:
        #if True or settings.BYPASS_OAUTH == True:
	if key.find('tpi.pearsoncmg.com') != -1 or key.find('tpicert.pearsoncmg.com') != -1 :
            return True;
        return params['oauth_signature'] == oauth_sig(settings.LAUNCH_METHOD, url, params, key)
    except:
        return params['oauth_signature'] == oauth_sig(settings.LAUNCH_METHOD, url, params, key)


def submit_outcome(params, **extra_params):
    import time
    extra_params.update({
        'transactionId': uuid.uuid4(),
        'dataSourceName': 'GL',
        'timeStamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
	#'timeStamp': '2018-01-05 01:01:01',
    })
    url = settings.OUTCOMES_URL
    body = outcome_xml(params, **extra_params)
    auth = (settings.OUTCOMES_USER, settings.OUTCOMES_PW)
    print 'body:', body
    resp = requests.post(url, data=body, auth=auth)
    time.sleep(1) 
    print 'resp:', resp, resp.content
    return resp
    
def timestamp():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

#iState must be an InteractiveState object.  This method sends a report to TPI
def sendTPIReport(iState, numLevels):
    
    params = json.loads(iState.iSession.launchParam)
    levels = InteractiveLevel.objects.filter(parent=iState, completed=True)        
    score = 0;
    for l in levels:
        score += l.score
    score = float(score)/100

    completedLevels = InteractiveLevel.objects.filter(Q(restarted=True) | Q(completed=True), parent=iState)
    count = len(completedLevels)/numLevels
    if len(completedLevels) % numLevels > 0:
        count += 1
    duration = 0
    for l in completedLevels:
        duration += int((l.closed - l.started).seconds)
    extraParam = {
    
        'transactionId':uuid.uuid4(),                    
        'timeStamp': timestamp(),
        'score':score,
        'duration':duration,
        'submissionCount':count,
        'problem_guid':params['custom_target_' + params['custom_currentquestion']],
        'problemNumber':params['custom_currentquestion'],
        'dataSourceName':'UE',
    }    
    
    url = settings.OUTCOMES_URL
    body = outcome_xml(params, **extraParam)
    auth = (settings.OUTCOMES_USER, settings.OUTCOMES_PW)
    print 'body:', body
    msg = TPI_Launch_Log(message=body)
    msg.save()
    resp = requests.post(url, data=body, auth=auth)
    print 'resp:', resp, resp.content
    print body
    return resp



if __name__ == '__main__':
    # print outcome_xml(TEST_TPI_PARAMS, TEST_EXTRA_PARAMS)
    # sig = oauth_sig('POST', 'http://gldata.redhillstudios.com/gllaunch/toolLaunch/', TEST_TPI_PARAMS)
    # print 'SIG:', sig
    # for (k, v) in TEST_TPI_PARAMS.iteritems():
    #     print k+'='+v
    url = settings.OUTCOMES_URL
    body = outcome_xml(TEST_TPI_PARAMS, **TEST_EXTRA_PARAMS)
    print 'body:', body
    resp = requests.post(url, data=body, auth=(settings.OUTCOMES_USER, settings.OUTCOMES_PW))
    print 'resp:', resp, resp.content
