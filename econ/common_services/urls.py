'''
Created on 15-Apr-2016

@author: naveen@knowdl.com
'''
from django.conf.urls import patterns, url
from econ.common_services.views import getQlSimAllData,getQlSimShortData, NavGethttpR,\
    getFredData,initAttemptData, saveAttemptData, getAttemptData, getLastAttemptData,\
    getAllAttemptData, getQlSimDuplicateEntries, updateQlSimDuplicateEntries,\
    getAttemptCount, getQlSimIncorrectData, getQlSimIncorrectDataCount,\
    updateQlSimIncorrectData, postGradeQlSimIncorrectData,\
    updateQlSimIncorrectDataId, postGradeQlSimIncorrectDataId, importCsvData2,\
    gettableCount, deletetableData, updateQuesAttemptDetails,\
    getupdateQuesAttemptDetails, importCsvData4, getDuplicateMAttempts,\
    updateDuplicateMAttempts, GetAssignmentData,\
    exportAssignJSON,exportAttemptJSON,getClassAverage, testmaria
 
urlpatterns = patterns(
 '',
 url(r'^testmaria/$', testmaria),
 url(r'^get_fred_data/$', getFredData),
 url(r'^init_qlsim_attempt_data/$', initAttemptData),
 url(r'^save_qlsim_attempt_data/$', saveAttemptData),
 url(r'^get_qlsim_duplicate_entries/$', getQlSimDuplicateEntries),
 url(r'^update_qlsim_duplicate_entries/$', updateQlSimDuplicateEntries),
 url(r'^get_qlsim_attempt_data/$', getAttemptData),
 url(r'^get_qlsim_lastattempt_data/$', getLastAttemptData),
 url(r'^get_qlsim_allattempt_data/$', getAllAttemptData),
 url(r'^get_qlsim_attempt_count/$', getAttemptCount),
 url(r'^navgethttpr/$', NavGethttpR),
 url(r'^get_qlsim_all_data/$', getQlSimAllData),
 url(r'^get_qlsim_short_data/$', getQlSimShortData), 
 url(r'^get_incorrect_data/$', getQlSimIncorrectData),
 url(r'^update_incorrect_data/$', updateQlSimIncorrectData),
 url(r'^postgrade_incorrect_data/$', postGradeQlSimIncorrectData),
 url(r'^update_incorrect_data_id/$', updateQlSimIncorrectDataId),
 url(r'^postgrade_incorrect_data_id/$', postGradeQlSimIncorrectDataId),
 url(r'^get_incorrect_data_count/$', getQlSimIncorrectDataCount),
 url(r'^import_csv2/$', importCsvData2),
 url(r'^get_table_count/$', gettableCount),
 url(r'^delete_table_data/$', deletetableData),
 url(r'^update_ques_att_data/$', updateQuesAttemptDetails),
 url(r'^get_update_ques_att_data/$', getupdateQuesAttemptDetails),
 url(r'^import_csv4/$', importCsvData4),
 url(r'^get_dup_attempt_data1/$', getDuplicateMAttempts),
 url(r'^update_dup_attempt_data/$', updateDuplicateMAttempts),
 url(r'^get_asgn_data_test/$', GetAssignmentData),
 #url(r'^migrateToFile/$', migrateAttemptDataToFile),
 #url(r'^compressQLAttData/$', compressQLAttData),
 url(r'^export_assign_json/$', exportAssignJSON),
 url(r'^export_attempt_json/$', exportAttemptJSON),
 url(r'^get_class_average/$', getClassAverage)
)






#end of file



