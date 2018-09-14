'''
Created on Jun 18, 2013

@author: charlieb
'''

LAUNCH_TEMPLATE = '''

<html>
 <head>
 </head>
  <body>
  <h1>{title}</h1>
   <div id="ltiLaunchFormSubmitArea">
     <form action="http://localhost:8000/gllaunch/toolLaunch/"
      name="ltiLaunchForm" id="ltiLaunchForm" method="post" encType="application/x-www-form-urlencoded">
       {inputs}
    <input type="submit" value="Simulate Launch"/>
     </form>
    </div>
     <script language="javascript">
      // document.getElementById("ltiLaunchFormSubmitArea").style.display = "none";
      // document.ltiLaunchForm.submit();
     </script>
  </body>
</html>
'''

GLV2_HOMEWORK_1_DO = {
"custom_lastname":"Tester",
"custom_course_id":"urn:udson:pearson.com/xl/devdb:course/138261_xlnoedx_devdb",
"context_id":"urn:udson:pearson.com/xl/devdb:course/138261",
"custom_originating_partner":"xl",
"custom_mode":"do",
"custom_savevalues":"1",
"custom_assignmenttitle":"GLv2 Homework 1",
"tool_consumer_instance_guid":"TPI",
"oauth_signature":"8wA6MDjZI1L6pG12b/oSfaljlBg=",
"lti_message_type":"basic-lti-launch-request",
"custom_print":"1",
"custom_totalpoints":"4",
"user_id":"urn:udson:pearson.com/xl/devdb:user/35870",
"custom_partnerId":"xlnoedx",
"custom_resource_id":"urn:udson:pearson.com/xl/devdb:homework/1800620",
"custom_tool_proxy_guid":"c2244900-8605-4ed2-8430-c26c838a19da",
"custom_questiontitle_1":"glv2-question1 (dev)",
"custom_currentquestion":"1",
"custom_questiontitle_3":"glv2-question3 (dev)",
"custom_questiontitle_2":"glv2-question2 (dev)",
"custom_partialcredit":"1",
"custom_institutionId":"devdb",
"custom_resultid":"urn:udson:pearson.com/xl/devdb:partnerhomeworkresult/43804",
"custom_target_1":"GL0001",
"custom_person_id":"gl-instructor",
"oauth_nonce":"7229886465741845923",
"oauth_timestamp":"1371601236",
"custom_points_3":"1",
"custom_points_2":"1",
"custom_points_1":"1",
"oauth_signature_method":"HMAC-SHA1",
"custom_points_4":"1",
"oauth_version":"1.0",
"custom_displaycourseid":"02Y1OL501Y2QD0",
"resource_link_id":"UNKNOWN",
"custom_target_3":"GL0003",
"custom_target_2":"GL0002",
"custom_target_4":"GL0004",
"roles":"Educator",
"context_type":"CourseSection",
"lti_version":"LTI-1p0",
"custom_membershipslastupdated":"2013-01-22T18:09:22.893Z",
"custom_handler_urn":"pearson/xlnoedx_phgl2/slink/x-pearson-xlnoedx_phgl2",
"custom_firstname":"GL",
"custom_questiontitle_4":"glv2-question4 (dev)",
"custom_attemptsallowed":"0",
"oauth_consumer_key":"TPI",
"custom_dateavailable":"2013-05-31T00:00:00Z",
}



def construct_mock_html(launch_dict, title):
    inputs = ''
    for k,v in launch_dict.items():
        inputs += '          <input name="{key}" value="{val}" type="hidden" />\n'.format(key=k, val=v)
    return LAUNCH_TEMPLATE.format(inputs=inputs, title=title)
    
if __name__=='__main__':
    s = construct_mock_html(GLV2_HOMEWORK_1_DO, "Captured TPI Launch, DO")
    with open('../../../generalLedger/app/mockLaunchDo_HM1.html', 'w') as f:
        f.write(s)
        
    