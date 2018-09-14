from django.http import HttpResponse
import csv, json, re
import io
from datetime import datetime
from media_library.views import index as medialibraryIndex


def index(request):
    return HttpResponse("Enter")


csv_model_keyvalue = {"Record ID": "record_id", "Record Title": "record_title", "Video URL": "video_url",
                      "Video Creation Date": "video_creation_date", "Video Length": "video_length",
                      "MetaData (keywords)": "metadata", "Recomendation Grouping": "recommendation",
                      "Primary?": "prime_video", "Video Info": "video_info", "Custom Target": "custom_target"}
question_csv_title = ["MCQ#",	"CorrectAnswer", "Distracter"]

import os 
def Aimportcsvtotable(request):
    dir_path = os.getcwd()
    return HttpResponse(dir_path)

def importcsvtotable(request):
    question_json = getquestionjson()
    with io.open('/opt/data/app1/knanalytics/importcsv/BMLRecordsLibraryConverter.csv', mode="r", encoding="utf-8") as csvfile:
        csv_table = csv.DictReader(csvfile, delimiter=',')
        media_table_values = []
        assignment_table_values = []

        from django.db import connection,transaction
        cursor = connection.cursor()
        for row in csv_table:
            media_sql_statement = 'INSERT INTO MediaLibrary('
            assignment_sql_statement = 'INSERT INTO MediaAssignments('
            m_column_type_string = ') VALUES ('
            a_column_type_string = ') VALUES ('
            m_column_values_str = []
            a_column_values_str = []
            question_dict = {}

            for col in row:
                for key in csv_model_keyvalue:
                    if key == col:
                        media_sql_statement = media_sql_statement + csv_model_keyvalue[key] + ","
                        if key == "Record ID":
                            m_column_values_str.append(int(row[col]))
                        elif key == "Video Creation Date":
                            end_date = row[col]
                            end_date = end_date.split(" ")
                            end_date[-1] = end_date[-1]
                            end_date = " ".join(end_date)
                            if len(end_date) == 4:
                                datetime_object = datetime.strptime(end_date, '%Y')
                            else:
                                datetime_object = datetime.strptime(end_date, '%Y %B')
                            m_column_values_str.append(datetime_object)
                        else:
                            colval = re.sub("'", "", row[col])
                            colval = re.sub("\n", "", colval)
                            m_column_values_str.append(re.sub("'", "", colval))

                        if key == "Record ID":
                            assignment_sql_statement = assignment_sql_statement + "media_" + csv_model_keyvalue[key] + ","
                            a_column_values_str.append(int(row[col]))
                            a_column_type_string = a_column_type_string + "%s,"
                        elif key == "Custom Target":
                            assignment_sql_statement = assignment_sql_statement + csv_model_keyvalue[key] + ","
                            a_column_values_str.append(row[col])
                            a_column_type_string = a_column_type_string + "%s,"

                        m_column_type_string = m_column_type_string + "%s,"
                        if col == "Record Title":
                            question_json["RecordTitle"] = row[col]
                        if col == "Video URL":
                            question_json["VideoURL"] = row[col]

                question_json["RecordId"] = row["Record ID"]
                question_json["LandingPageURL"] = "record" + row["Record ID"] + ".html"
                question_json["LandingPageImage"] = "record" + row["Record ID"] + ".jpg"
                for item in question_csv_title:
                    colEdit = col.replace(" ", "", 3)
                    if bool(re.search(item, colEdit)):
                        question_dict[colEdit] = row[col]

            question_json = createquestionjson(question_dict, question_json)
            m_column_values_str.append(re.sub("'", "", json.dumps(question_json)))
            m_column_values_str.append('videoThumbnail' + row["Record ID"] + '.jpg')
            m_column_values_str.append('record' + row["Record ID"] + '_landingPage.html')
            m_column_values_str.append('record' + row["Record ID"] + '_landingImage.jpg')
            m_column_values_str = tuple(m_column_values_str)
            m_column_type_string = m_column_type_string + "%s,%s,%s,%s)"
            media_sql_statement = media_sql_statement + "media_mcq,video_thumbnail, landing_content,landing_image"
            media_table_values.append(m_column_values_str)

        m_final_statement = media_sql_statement + m_column_type_string

        try:
            cursor.executemany(m_final_statement, media_table_values)
            #devDB.escape_string(m_final_statement)

            #devDB.commit()
            transaction.commit()
            return medialibraryIndex(request)
        except Exception as e:
            print(e)
            return HttpResponse(e)


def getquestionjson():
    with open("/opt/data/app1/knanalytics/importcsv/modulejson.json") as data:
        json_data = data.read()
    json_dict = json.loads(json_data)
    return json_dict


def createquestionjson(question_dict, question_json):
    count = 0
    for item in question_json["Questions"]:
        question_json["Questions"][count]["QuestionText"] = question_dict["MCQ#" + str(count + 1)]
        question_json["Questions"][count]["Options"][0]["OptionText"] = question_dict["Q"+str(count + 1)+"CorrectAnswer"]
        question_json["Questions"][count]["Options"][1]["OptionText"] = question_dict["Q"+str(count + 1)+"DistracterA"]
        question_json["Questions"][count]["Options"][2]["OptionText"] = question_dict["Q"+str(count + 1)+"DistracterB"]
        question_json["Questions"][count]["Options"][3]["OptionText"] = question_dict["Q"+str(count + 1)+"DistracterC"]
        if question_dict["Q1DistracterD"] != "":
            question_json["Questions"][count]["Options"][0]["OptionText"] = question_dict["Q"+str(count + 1)+"DistracterD"]
        count = count + 1
    return question_json
