def GetQuestionDetailsModel(selsim, selloc, ASGN="", isStudentDetails=False):
    # 'unicode-escape' is used to escape sequences in string
    selsim = selsim.decode('unicode-escape')

    filter1 = {"QL_Id": selsim}
    lstQLMasterQ = m.ql_masterquestions.objects.filter(**filter1).all()
    packagerelPath = getOptionPath(selsim)
    '''
    if (packagerelPath.find('/qualsims') != -1):
        packagerelPath = packagerelPath.replace('/qualsims', 'content/qualsims/')   
    '''

    filter2 = {"QL_Id": selsim, 'ReportStatus': 'active'}
    qlMasterAttempts = None

    if ASGN:
        filter2["Assignment_Id"] = ASGN
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)
    else:
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)

    if qlMasterAttempts.count() == 0:
        return " No data found"

    lstQLMasterAttemptsId = qlMasterAttempts.values_list("Id")

    filter3 = {'MstAttemptId__in': lstQLMasterAttemptsId}
    lstQLQuestionAttemptDetails = m.ql_questionattemptdetails.objects.filter(
        **filter3).all()

    sameqs = []

    qlQDRV = Classes.QLQuestionDetailReportView()
    qlQDRV.Results = []

    for qlMqd in lstQLMasterQ:
        qlQDR = Classes.QLQuestionDetailReport()

        if qlMqd.QuestionText is not None:
            qlQDR.Text = qlMqd.QuestionText.encode("utf-8")

        qlQDR.Id = qlMqd.QuestionId
        qlQDR.OccurenceNo = ""

        if qlMqd.QuestionTitle is not None:
            qlQDR.QuestionTitle = qlMqd.QuestionTitle.encode("utf-8")
            # same question occurance no
            filtersmq = {'QL_Id': selsim, 'QuestionTitle': qlQDR.QuestionTitle}
            if m.ql_masterquestions.objects.filter(**filtersmq).count() > 1:
                supval = ""
                occrnc = sameqs.count(qlQDR.QuestionTitle) + 1
                qlQDR.OccurenceNo = str(occrnc)

                if occrnc == 1:
                    supval = "<sup>st</sup>"
                elif occrnc == 2:
                    supval = "<sup>nd</sup>"
                elif occrnc == 3:
                    supval = "<sup>rd</sup>"
                else:
                    supval = "<sup>th</sup>"

                qlQDR.OccurenceNo = " (" + qlQDR.OccurenceNo + \
                    supval + " instance)"
                sameqs.append(qlQDR.QuestionTitle)

        qlQDR.Points = str(int(qlMqd.TotalPoints))
        qlQDR.Options = []
        qlQDR.OptionAlignment = "V"

        if qlMqd.AdditionalInfo is not None and qlMqd.AdditionalInfo != '""':
            qlQDR.OptionAlignment = "V"
            # str(jsonObjDetail["OptionAlignment"])
        # end if qlMqd.AdditionalInfo

        filter4 = {"QuestionId": qlMqd.QuestionId}
        lstattemptedforQuestion = lstQLQuestionAttemptDetails.filter(**filter4)
        lstattemptedforQuestionId = lstQLQuestionAttemptDetails.values(
            "MstAttemptId").distinct()

        if isStudentDetails:
            qlQDR.Students = []
            filterstd = {'Id__in': lstattemptedforQuestionId}
            lstMasterQsnAttempt = qlMasterAttempts.filter(**filterstd).all()
            for qma in lstMasterQsnAttempt:
                student = Classes.QLStudentDetails()
                student.Name = qma.StudentName
                student.Id = qma.Student_Id
                student.MasterAttemptId = qma.Id
                filterques = {'MstAttemptId': qma.Id,
                              'QuestionId': qlMqd.QuestionId}
                # print lstattemptedforQuestion.count()
                if lstattemptedforQuestion.count() > 0:
                    studentQAttempt = lstattemptedforQuestion.filter(
                        **filterques).values_list("Points").all()
                    if studentQAttempt:
                        # print studentQAttempt
                        student.Points = str(int(studentQAttempt[0][0]))
                        qlQDR.Students.append(student)
        # end if isStudentDetails

        # no of times question answered
        qlQDR.NumberOfTimesAnswered = lstattemptedforQuestion.count()
        qlQDR.QuestionAttempted = str(qlQDR.NumberOfTimesAnswered)

        # no of time question attempted
        ttlAttmpt = lstQLMasterAttemptsId.count()
        qlQDR.TotalAttempted = str(ttlAttmpt)

        if ttlAttmpt > 0:
            qlQDR.Presented = str(
                int(float(qlQDR.NumberOfTimesAnswered) / float(ttlAttmpt) * 100)) + "%"
        else:
            qlQDR.Presented = "0" + "%"

        if qlQDR.NumberOfTimesAnswered > 0:
            avgscr = lstattemptedforQuestion.aggregate(Avg('Score'))
            if avgscr.__len__() > 0:
                qlQDR.AverageScorePercent = str(int(avgscr["Score__avg"]))
            else:
                qlQDR.AverageScorePercent = "0"
        else:
            qlQDR.AverageScorePercent = "0"

        lstqloption = []
        correctCnt = 0
        incorrectCnt = 0
        partialCorrCnt = 0

        if qlMqd.Options == "" or qlMqd.Options == '[""]' or qlMqd.Options == '[]':
            pass
        else:
            try:
                lstqloption = literal_eval(qlMqd.Options)
            except Exception:
                pass

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

                filter5 = {"SelOptionId": seloptid}
                qlOptionReport.NumberOfTimesAnswered = lstattemptedforQuestion.filter(
                    **filter5).count()

                percent = 0
                if qlOptionReport.NumberOfTimesAnswered > 0:
                    percent = (float(qlOptionReport.NumberOfTimesAnswered) /
                               float(qlQDR.NumberOfTimesAnswered)) * 100

                if percent > 0:
                    qlOptionReport.Percent = str(round(percent, 2)) + "%"

                if qlOptionReport.Status.lower() == "correct" and qlOptionReport.NumberOfTimesAnswered > 0:
                    correctCnt += 1

                if qlOptionReport.Status.lower() == "incorrect" and qlOptionReport.NumberOfTimesAnswered > 0:
                    incorrectCnt += 1

                if qlOptionReport.Status.lower() == "partial" and qlOptionReport.NumberOfTimesAnswered > 0:
                    partialCorrCnt += 1

                if qlOptionReport.Points >= 5:
                    qlOptionReport.PointsImage = k_ANALYTICS_STATIC + "images/5point.png"
                else:
                    qlOptionReport.PointsImage = k_ANALYTICS_STATIC + \
                        "images/" + str(qlOptionReport.Points) + "point.png"

                qlQDR.Options.append(qlOptionReport)
        # for qloption in lstqloption ends

        # question graph
        qlQDR.ForGraph = str(qlQDR.NumberOfTimesAnswered) + "###" + str(
            correctCnt) + "###" + str(incorrectCnt) + "###" + str(partialCorrCnt)

        qlQDRV.Results.append(qlQDR)
    #for qlMqd in lstQLMasterQ : ends

    if qlQDRV.Results.__len__() > 0:

        totalattempts = qlMasterAttempts.count()

        filterComp = {"CompletionStatus": "complete"}
        totalcompleted = qlMasterAttempts.filter(**filterComp).count()
        # print " totalcompleted " + str(totalcompleted )
        compltcnt = 0
        if totalattempts > 0:
            compltcnt = int(float(totalcompleted) / float(totalattempts) * 100)

        qlQDRV.AverageCompleted = float(compltcnt)
        # print " compltcnt " + str(compltcnt )

        filterscr = {"CompletionStatus": "complete", "Score__isnull": False}
        scorelist = qlMasterAttempts.filter(**filterscr).values("Score").all()
        if scorelist.count() > 0:
            # print scorelist
            qlQDRV.AverageScore = qlMasterAttempts.filter(
                **filterscr).aggregate(Avg('Score'))["Score__avg"]
            qlQDRV.MedianScore = getMedian(scorelist)
        else:
            qlQDRV.AverageScore = 0
            qlQDRV.MedianScore = 0
    else:
        qlQDRV.AverageScore = 0
        qlQDRV.MedianScore = 0
        qlQDRV.AverageCompleted = 0
    return qlQDRV
