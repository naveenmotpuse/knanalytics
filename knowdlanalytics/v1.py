def GetStudentDetailModel(selsim, selloc, ASGN=""):
    selsim = selsim.decode('unicode-escape')
    filter1 = {"QL_Id": selsim}
    lstQLMasterQ = m.ql_masterquestions.objects.filter(**filter1).all()
    packagerelPath = getOptionPath(selsim)
    filter2 = {"QL_Id": selsim, 'ReportStatus': 'active'}
    qlMasterAttempts = None

    if ASGN:
        filter2["Assignment_Id"] = ASGN
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)
    else:
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)

    if qlMasterAttempts.count() == 0:
        return "No data found"

    lstQLMasterAttemptsId = qlMasterAttempts.values_list("Id")

    filter3 = {'MstAttemptId__in': lstQLMasterAttemptsId}
    lstQLQuestionAttemptDetails = m.ql_questionattemptdetails.objects.filter(
        **filter3).all()

    qlSRV = Classes.QLStudentReportView()
    qlSRV.Results = []  # List<QLStudentDetails>()
    qlSRV.QuestionsDetails = []  # List<QlQuestionMasterForStudentReport>()

    for qlMa in qlMasterAttempts:
        student = Classes.QLStudentDetails()
        stuattempts = None
        student.Name = qlMa.StudentName
        student.Id = qlMa.Student_Id
        student.MasterAttemptId = qlMa.Id
        student.Score = 0.0 if qlMa.Score is None else qlMa.Score
        student.CompletionStatus = "Completed" if qlMa.CompletionStatus == "complete" else "In Progress"

        stuattempts = None

        filterSAttmpt = {"QL_Id": selsim, 'CompletionStatus': 'complete'}
        if ASGN:
            filterSAttmpt["Student_Id"] = qlMa.Student_Id
            filterSAttmpt["Assignment_Id"] = ASGN
            stuattempts = m.ql_masterattempts.objects.filter(
                **filterSAttmpt).all()
        else:
            stuattempts = m.ql_masterattempts.objects.filter(
                **filterSAttmpt).all()

        student.Attempts = []  # List<QLStudentAttempt>()
        if stuattempts is not None and stuattempts.count() > 0:
            k = 1
            for std in stuattempts:
                statt = Classes.QLStudentAttempt()
                statt.AttemptNo = k
                statt.Score = 0.00 if std.Score is None else std.Score
                statt.SessionId = std.Session_Id
                student.Attempts.append(statt)
                k = k + 1
        # end if stuattempts is not None and stuattempts.count() > 0 :

        student.Questions = []  # List<QLQuestionForStudentReport>()
        filterSQues = {"MstAttemptId": qlMa.Id}
        studentQuestionsDetails = lstQLQuestionAttemptDetails.filter(
            **filterSQues).all()
        if studentQuestionsDetails and studentQuestionsDetails.count() > 0:
            sameqs = []
            for qlqd in studentQuestionsDetails:
                filterQues = {"QuestionId": qlqd.QuestionId}
                quesMasterLst = lstQLMasterQ.filter(**filterQues).all()
                quesMaster = quesMasterLst[0]
                if ObjectExistInArray(qlSRV.QuestionsDetails, "Id", qlqd.QuestionId) is False:
                    question = Classes.QlQuestionMasterForStudentReport()
                    question.Id = qlqd.QuestionId.encode("utf-8")
                    question.OptionAlignment = "V"
                    if quesMaster.AdditionalInfo is not None and quesMaster.AdditionalInfo != '""' and quesMaster.AdditionalInfo != '' and quesMaster.AdditionalInfo != '{}':
                        jsonObjDetail = literal_eval(quesMaster.AdditionalInfo)
                        question.OptionAlignment = str(
                            jsonObjDetail["OptionAlignment"])

                    question.Text = quesMaster.QuestionText.replace(
                        "Select an option from the choices below and click Submit.", "")

                    lstqloption = []  # List<QlOption>()
                    if quesMaster.Options != "" and quesMaster.Options != '[""]' and quesMaster.Options != '[]':
                        try:
                            lstqloption = literal_eval(quesMaster.Options)
                        except Exception:
                            pass

                        #question.Options = lstqloption
                        for qloption in lstqloption:
                            qlOptionReport = Classes.QlOptionReport()
                            try:
                                qlOptionReport.Text = qloption["Text"]
                            except Exception as ine:
                                qlOptionReport.Text = ''

                            try:
                                qlOptionReport.Status = qloption["Status"]
                            except Exception as ine:
                                qlOptionReport.Status = ''

                            try:
                                qlOptionReport.Points = qloption["Points"]
                            except Exception as ine:
                                qlOptionReport.Points = "0"

                            try:
                                qlOptionReport.Image = packagerelPath + \
                                    "/" + qloption["Img"]
                            except Exception as ine:
                                qlOptionReport.Image = ""

                            # print qloption["Points"]
                            seloptid = ""
                            try:
                                seloptid = qloption["Id"]
                            except Exception as ine:
                                seloptid = ""
                            '''
                            filter5 = {"SelOptionId": seloptid}
                            qlOptionReport.NumberOfTimesAnswered = lstattemptedforQuestion.filter(
                                **filter5).count()

                            percent = 0
                            if qlOptionReport.NumberOfTimesAnswered > 0:
                                percent = (float(qlOptionReport.NumberOfTimesAnswered) /
                                        float(qlQDR.NumberOfTimesAnswered)) * 100
                            '''
                            if percent > 0:
                                qlOptionReport.Percent = str(round(percent, 2)) + "%"
                            '''
                            if qlOptionReport.Status.lower() == "correct" and qlOptionReport.NumberOfTimesAnswered > 0:
                                correctCnt += 1

                            if qlOptionReport.Status.lower() == "incorrect" and qlOptionReport.NumberOfTimesAnswered > 0:
                                incorrectCnt += 1

                            if qlOptionReport.Status.lower() == "partial" and qlOptionReport.NumberOfTimesAnswered > 0:
                                partialCorrCnt += 1
                            '''

                            if qlOptionReport.Points >= 5:
                                qlOptionReport.PointsImage = k_ANALYTICS_STATIC + "images/5point.png"
                            else:
                                qlOptionReport.PointsImage = k_ANALYTICS_STATIC + \
                                    "images/" + str(qlOptionReport.Points) + "point.png"

                            question.Options.append(qlOptionReport)
                        #end option

                    question.OccurenceNo = ""

                    if quesMaster.QuestionTitle is not None:
                        question.QuestionTitle = quesMaster.QuestionTitle.encode(
                            "utf-8")
                        # same question occurance no
                        filtersmq = {'QL_Id': selsim,
                                     'QuestionTitle': question.QuestionTitle}
                        if m.ql_masterquestions.objects.filter(**filtersmq).count() > 1:
                            supval = ""
                            occrnc = sameqs.count(question.QuestionTitle) + 1
                            question.OccurenceNo = str(occrnc)

                            if occrnc == 1:
                                supval = "<sup>st</sup>"
                            elif occrnc == 2:
                                supval = "<sup>nd</sup>"
                            elif occrnc == 3:
                                supval = "<sup>rd</sup>"
                            else:
                                supval = "<sup>th</sup>"

                            question.OccurenceNo = " (" + \
                                question.OccurenceNo + supval + " instance)"
                            sameqs.append(question.QuestionTitle)
                        # if end question occ more that once
                    # end if qlqd.QuestionTitle is not None
                    qlSRV.QuestionsDetails.append(question)
                # if end ObjectExistInArray
                qlquestion = Classes.QLQuestionForStudentReport()
                qlquestion.Id = qlqd.QuestionId
                qlquestion.PointsObtained = int(qlqd.Points)
                qlquestion.TotalPoints = int(quesMaster.TotalPoints)
                qlquestion.SelectedOption = qlqd.SelOptionId

                if int(qlqd.Points) >= 5:
                    qlquestion.PointsImage = k_ANALYTICS_STATIC + "images/5point.png"
                else:
                    qlquestion.PointsImage = k_ANALYTICS_STATIC + "images/" + \
                        str(qlquestion.PointsObtained) + "point.png"

                student.Questions.append(qlquestion)
            # endfor qlqd in studentQuestionsDetails :

        qlSRV.Results.append(student)

    # endfor qlMa in qlMasterAttempts :

    if qlSRV.Results.__len__() > 0:
        filterscr = {"CompletionStatus": "complete", "Score__isnull": False}
        scorelist = qlMasterAttempts.filter(**filterscr).values("Score").all()
        if scorelist.count() > 0:
            # print scorelist
            qlSRV.AverageScore = qlMasterAttempts.filter(
                **filterscr).aggregate(Avg('Score'))["Score__avg"]
        else:
            qlSRV.AverageScore = 0
    else:
        qlSRV.AverageScore = 0

    return qlSRV