var Utility = function () {
    return {
        shuffle: function (e) {
            for (var t, n, r = e.length; 0 !== r;) n = Math.floor(Math.random() * r), r -= 1, t = e[r], e[r] = e[n], e[n] = t;
            return e
        },
        getParameterByName: function (e, t) {
            e = e.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
            var n = new RegExp("[\\?&]" + e + "=([^&#]*)"),
                r = n.exec(t);
            return null === r ? "" : decodeURIComponent(r[1].replace(/\+/g, " "))
        },
        updateHtml: function (e, t) {
            $.each(e, function (e, n) {
                var r = "",
                    a = $(n);
                $.each(t, function (e, t) {
                    var n = new RegExp(e, "g");
                    r += a.html().replace(n, t)
                }), a.html(r)
            })
        },
        mergeArray: function (e, t) {
            var n = e.concat(t).sort(function (e, t) {
                return e > t ? 1 : t > e ? -1 : 0
            });
            return n.filter(function (e, t) {
                return n.indexOf(e) === t
            })
        },
        injectCss: function (e) {
            var t = document.getElementsByTagName("head")[0],
                n = document.createElement("style");
            n.setAttribute("type", "text/css"), n.styleSheet ? n.styleSheet.cssText = e : n.appendChild(document.createTextNode(e)), t.appendChild(n)
        },
        getRandomIntInclusive: function (e, t) {
            return Math.floor(Math.random() * (t - e + 1)) + e
        },
        getAbbrNum: function (e, t, n, r) {
            if (0 > e) var a = -1;
            else var a = 1; - 1 == a ? (a = "-", e = Math.abs(e)) : a = "", t = Math.pow(10, t);
            for (var o = ["k", "m", "b", "t"], c = o.length - 1; c >= 0; c--) {
                var u = Math.pow(10, 3 * (c + 1));
                if (e >= u) {
                    e = Math.round(e * t / u) / t, 1e3 == e && c < o.length - 1 && (e = 1, c++), e += o[c];
                    break
                }
            }
            return a + n + e
        },
        removeDuplicates: function (originalArray, objKey) {
            var trimmedArray = [];
            var values = [];
            var value;
            for (var i = 0; i < originalArray.length; i++) {
                value = originalArray[i][objKey];
                if (values.indexOf(value) === -1) {
                    trimmedArray.push(originalArray[i]);
                    values.push(value);
                }
            }
            return trimmedArray;
        },
        hasDuplicates: function (originalArray, objKey) {
            var hsDup = false;
            var values = [];
            var value;
            for (var i = 0; i < originalArray.length; i++) {
                value = originalArray[i][objKey];
                if (values.indexOf(value) === -1) {
                    values.push(value);
                } else {
                    hsDup = true;
                    break;
                }
            }
            return hsDup;
        }
    }
}();

if (gRMAttemptData == undefined) gRMAttemptData = {};
gRMAttemptData.Async = "true";
var moduleStartPage = 95;

var LaunchMode = {
    "do": "do",
    review: "review",
    setup: "setup",
    presenter: "presenter",
    preview: "preview"
}
var UserRoles = {
    learner: "learner",
    author: "author",
    presenter: "presenter",
    educator: "educator"
}
var navlastpage = 1;
//nav - i think we need this condition here...
if (typeof (isModuleLoaded) === 'undefined') {
    //if (typeof skipped_GetSessionData == 'undefined' || skipped_GetSessionData == false) {
    var g_TPIDuration = 0;
    var g_requestNo = 0;

    //NM:21-July-2017 - bookmark page logic is changed from page index to page Id.
    var attempt = {
        //"no": 1,
        "status": "new",
        "duration": 0,
        "overallScore": 0,
        "lastVisitedPgIndex": 0,
        "lastVisitedPgId": "",
        "maxscore": -1,
        "reqdData": {},
        "startDate": new Date()
    };

    // Global TPI data
    var TPIAttempts = {}; // save q-a data
    var TPIData = {};
    TPIData.SessionId = 0;
    TPIData.SessionData = {};
    TPIData.Mode = 'do';
    TPIData.Roles = '';
    TPIData.CurrentQuestion = '';
    TPIData.TargetId = '';
    TPIData.ResourceId = '';
    TPIData.SessionObj = {};
    TPIData.Sessionstate = {};
    TPIData.TargetPoints = 1
    TPIData.AllowedAttempts = 0;
}

if (gPackageType == 'Presenter') {
    TPIData.Roles = 'Presenter';
}

//Time starts now 
var _startTime = new Date();
if (typeof (isModuleLoaded) === 'undefined') {
    var KnowdlTracking = (function () {
        var _data = {}
        _data.CompletionStatus = "Inprogress";
        var _globals = {}

        //var _knowdlPostUrl = "http://dev.knowdl.com/qlinteraction/process";
        //var _knowdlPostUrl = "https://stage1.knowdl.com/qlinteraction/process"
        var _knowdlPostUrl =  window.location.origin + "/knowdlanalytics/QLInteractionProcess/"

        var _questionstarttime = new Date();

        var _classAverage = 0;

        var _MQAdditionalInfo = [];
        var QL_Settings = {
            IsQualsim: true,
            CA_Dial_Off_SR: false
        }

        return {
            get_Settings: function () {
                return QL_Settings;
            },
            set_Settings: function (setObj) {
                if (setObj.IsQualsim) {
                    QL_Settings = setObj;
                }
            },
            InitLaunch: function (_skipPostData) {
                var skipInit = false;
                if ((_skipPostData + "") == "true") {
                    skipInit = true;
                }

                _questionstarttime = _startTime;
                if (TPIData.SessionData != undefined && TPIData.SessionData.launch_data != undefined) {
                    //_globals.QL_Id = TPIData.SessionData.launch_data["context_id"];
                    _globals.QL_Id = TPIData.SessionData.launch_data['custom_target_' + TPIData.SessionData.launch_data.custom_currentquestion];
                    _globals.QLTitle = TPIData.SessionData.launch_data["custom_questiontitle_" + TPIData.SessionData.launch_data.custom_currentquestion];
                    _globals.Assignment_Id = TPIData.SessionData.launch_data["custom_resource_id"];
                    _globals.AssignmentLocation = window.location.hostname;
                    _globals.AssignmentTitle = TPIData.SessionData.launch_data["custom_assignmenttitle"];
                    _globals.Student_Id = TPIData.SessionData.launch_data["user_id"];
                    _globals.Session_Id = TPIData.SessionId;
                    _globals.StudentName = TPIData.SessionData.launch_data["custom_firstname"] + " " + TPIData.SessionData.launch_data["custom_lastname"];
                    _globals.Role = TPIData.SessionData.launch_data["roles"];
                    _globals.NumberOfAttempts = TPIData.SessionData.launch_data["custom_attemptsallowed"];
                    _globals.TargetPoints = TPIData.SessionData.launch_data["custom_points_" + TPIData.SessionData.launch_data.custom_currentquestion];
                    _globals.ObjectiveDetails = this.GetObjectiveDefinition();
                    //_globals.LevelsAssigned = visibleLevels;

                    //Handle Objectives show hide logic.
                    QLSimUser = _globals.QL_Id.split("/")[_globals.QL_Id.split("/").length - 1]

                    if (!skipInit) {
                        this.PostLaunchData();
                    }
                }

            },
            //nav - educator preview
            HandlePreviewMode: function () {

                var simurl = document.URL;
                var suffix = "/";
                var getsimurlLastItem = simurl.slice(-1);
                if (getsimurlLastItem == suffix) {
                    simurl = simurl.substring(0, simurl.length - 1)
                }
                //if (simurl.endsWith("/"))
                //simurl = simurl.substring(0, simurl.length - 1)

                var simurlarr = simurl.split("/");
                var mediaUser = "";
                if (simurlarr.length > 1) {
                    if (simurlarr[simurlarr.length - 2].toLowerCase() == "preview") {
                        mediaUser = simurlarr[simurlarr.length - 1];
                        QLSimUser = mediaUser;
                        TPIData.Mode = LaunchMode.preview;

                        for (var i = 0; i < ObjectiveDefinitions.length; i++) {
                            //Commented for now to run locally 
                            var objuser = ObjectiveDefinitions[i].CustomTarget.split("/")[ObjectiveDefinitions[i].CustomTarget.split("/").length - 1];
                            if (objuser == mediaUser) {
                                _globals.QL_Id = ObjectiveDefinitions[i].CustomTarget;
                                break;
                            }
                        }

                        if (mediaUser == "") {
                            _globals.QL_Id = ObjectiveDefinitions[0].CustomTarget;
                            QLSimUser = ObjectiveDefinitions[0].CustomTarget.split("/")[ObjectiveDefinitions[0].CustomTarget.split("/").length - 1]
                        }
                    }
                }
            },
            GetObjectiveDefinition: function () {
                var objective = "";
                if (knowdldebugMode) debugger;
                if (_globals.QL_Id == undefined || _globals.QL_Id == "") {
                    _globals.QL_Id = "qualsims/marketing/marketing-mix/kotler";
                }
                for (var i = 0; i < ObjectiveDefinitions.length; i++) {
                    //Commented for now to run locally            
                    if (ObjectiveDefinitions[i].CustomTarget == _globals.QL_Id) {
                        objective = ObjectiveDefinitions[i];
                        break;
                    }
                }
                return objective;
            },
            GetQTitleFromMenu: function (paramPgId) {
                var local_qTitle = "";
                if (MenuData != undefined && MenuData.length > 0) {
                    for (var i = 0; i < MenuData.length; i++) {
                        if ((MenuData[i].PageId + '') == (paramPgId + '')) {
                            local_qTitle = MenuData[i].MenuTitle;
                            break;
                        }
                    }
                }
                return local_qTitle;
            },
            GetMQAdditionalInfo: function (paramqId) {
                var retObj = "";

                for (var i = 0; i < _MQAdditionalInfo.length; i++) {
                    if ((_MQAdditionalInfo[i].QId + '') == (paramqId + '')) {
                        retObj = JSON.parse(JSON.stringify(_MQAdditionalInfo[i].Info));
                        break;
                    }
                }

                return retObj;
            },
            //NM:10Sep - stage1 avg score dependency removal.
            //Updated this method to call get avgscore from econdip server.
            //This method is called from KnowdlTracking.SetCompletion() and _graphUtility.drawPieChartB()
            getClassAverage: function (updateandget) {
                if (knowdldebugMode) debugger;
                if (IsRevel()) {
                    return;
                }
                var maxscore = TPIAttempts.Attempts[TPIAttempts.Attempts.length - 1].maxscore;
                if (maxscore == undefined) {
                    maxscore = -1;
                }
                maxscore = Number(maxscore)
                var score = QLSimModule.GetTotalScore();
                if (score == undefined) {
                    score = 0;
                }
                score = Number(score)
                var scoreDiff = -1;
                if (maxscore == -1) {
                    if (updateandget != undefined && updateandget == "updateandget") {
                        scoreDiff = score;
                    }
                } else if (score > maxscore) {
                    if (updateandget != undefined && updateandget == "updateandget") {
                        scoreDiff = (score - maxscore);
                    } else {
                        scoreDiff = -1;
                    }
                } else {
                    scoreDiff = -1;
                }
                _classAverage = ServiceCalls.get_class_average(_globals.QL_Id, _globals.Assignment_Id, maxscore, scoreDiff)
                return _classAverage;
            },
            PostQuestionData: function (qObj) {
                //this method is called in UpdateAttemptMaxScore->UpdateUserAttempts to post question data
                //Need to call on pages where UpdateAttemptMaxScore is not called.
                if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                    QDetails = {};
                    if (qObj != undefined && qObj != null) {
                        QDetails.QId = qObj.QId;
                        QDetails.PId = qObj.PId;
                        QDetails.QText = qObj.QText;
                        QDetails.QOptions = qObj.QOptions;
                        QDetails.QSelOptionId = qObj.QSelOptionId;
                        QDetails.QTotal = qObj.QTotal;
                        QDetails.QPoints = qObj.QPoints;
                        QDetails.QCorrectStatus = qObj.QCorrectStatus;
                        QDetails.QTitle = qObj.QTitle;

                        var tempQTitle = this.GetQTitleFromMenu(qObj.PId);
                        if (tempQTitle != undefined && tempQTitle != "") {
                            QDetails.QTitle = tempQTitle;
                        }

                        if (QDetails.QTotal == undefined) {
                            QDetails.QTotal = 1;
                        }

                        QDetails.QScore = (Number(QDetails.QPoints) / Number(QDetails.QTotal)) * 100;
                        if (QDetails.QScore == undefined || QDetails.QScore == null) {
                            QDetails.QScore = 0;
                            QDetails.QPoints = 0;
                        } else {
                            QDetails.QScore = Number(Number(QDetails.QScore).toFixed(2));
                        }
                        QDetails.MQAdditionalInfo = this.GetMQAdditionalInfo(qObj.QId);
                        QDetails.AdditionalInfo = qObj.AdditionalInfo;
                    }
                    _data.QDetails = QDetails;

                    //Qtimespent is calculated in post data.
                    this.PostData();
                }
            },
            SetCompletion: function () {
                if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                    _data.QDetails = {};
                    _data.CompletionStatus = "complete";
                    this.PostData(false);
                    //NM:10Sep - stage1 avg score dependency removal.
                    //First call to getClassAverage() - Is to update score only when completion is marked.
                    this.getClassAverage("updateandget");
                }
            },
            RetryAttempt: function () {
                if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                    _data.QDetails = {};
                    _data.CompletionStatus = "inprogress";
                    g_TPIDuration = 0
                    this.InitLaunch();
                }
            },
            PostLaunchData: function (p_async) {
                if (IsRevel()) {
                    return;
                }
                var _async = true;
                if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                    if (p_async != undefined && p_async == false) {
                        _async = false;
                    }
                    var jsonSerialized = JSON.stringify(_globals);
                    //replace special characters.
                    //jsonSerialized = jsonSerialized.replace(/[^a-zA-Z ',"<>!~@#$%&*.+-=|\?()\[\]_{}\\ ]/g, "");
                    //var servcUrl = _knowdlPostUrl + "?command=launch";
                    var servcUrl = _knowdlPostUrl;
                    $.ajax({
                        type: "POST",
                        async: true,
                        url: servcUrl,
                        data: {
                            jsondata: jsonSerialized,
                            'command': 'launch'
                        },
                        success: function (result) {
                            //Data posted successfully
                        },
                        error: function (error) {

                        }
                    });
                }
            },

            PostData: function (p_async) {
                if (IsRevel()) {
                    return;
                }
                var _async = true;
                //if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do && (typeof g_reachedSummary == 'undefined' || g_reachedSummary == false)) {
                if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                    if (p_async != undefined && p_async == false) {
                        _async = false;
                    }
                    _data.QL_Id = _globals.QL_Id;
                    _data.Assignment_Id = _globals.Assignment_Id;
                    _data.Student_Id = _globals.Student_Id;
                    _data.AssignmentLocation = _globals.AssignmentLocation;

                    var currTime = new Date();

                    if (_data.QDetails != undefined) {
                        if (_data.QDetails.QId != undefined) {
                            _data.QDetails.QTimeSpent = parseInt((currTime.getTime() - _questionstarttime.getTime()) / 1000);
                        }
                    }

                    //Reset level start time 
                    _questionstarttime = currTime;

                    _data.OverallTimeSpent = parseInt((new Date().getTime() - _startTime.getTime()) / 1000) + g_TPIDuration;
                    _data.OverallScore = QLSimModule.GetTotalScore();

                    //overall points needs to be calculated.
                    _data.OverallPoints = QLSimModule.GetUserScore();
                    //end                

                    var jsonSerialized = JSON.stringify(_data);
                    //replace special characters.
                    //jsonSerialized = jsonSerialized.replace(/[^a-zA-Z ',"<>!~@#$%&*.+-=|\?()\[\]_{}\\ ]/g, "").replace(/&/g, '%26');
                    //var servcUrl = _knowdlPostUrl + "?command=updateattemptdata";
                    var servcUrl = _knowdlPostUrl;
                    $.ajax({
                        type: "POST",
                        async: true,
                        url: servcUrl,
                        data: {
                            jsondata: jsonSerialized,
                            'command': 'updateattemptdata'
                        },
                        success: function (result) {
                            //Data posted successfully
                        },
                        error: function (error) {

                        }
                    });

                    //reset Q Details
                    _data.QDetails = {}
                }
            }

        };
    })();
}

//5. Service calls Module
//++++++++++++++++++ Service calls ++++++++++++++++++
var reviewModeNo = 1;
var ServiceCalls = (function () {
    //URLs
    var _serviceurl = window.location.origin + "/econservice";
    //var _gradePostUrl = "http://cert.isb.lift.pearsoncmg.com/v1/dataexchange/tpi/submit";
    var atmptIndx = 0;

    return {
        getAttemptIndex: function () {
            return atmptIndx;
        },
        setAttemptIndex: function (_indx) {
            atmptIndx = _indx;
        },
        get_service_Url: function () {
            return _serviceurl;
        },
        set_reviewModeNoUsingHref: function () {
            if (Utility.getParameterByName("mode", window.location.href) === LaunchMode.review) {
                reviewModeNo = Number(Utility.getParameterByName("att", window.location.href));
            }
        },
        //NM:10Sep - stage1 avg score dependency removal.
        //Added new service to get avgScore from econdip server.
        //This function is called from KnowdlTracking.getClassAverage() method.
        get_class_average: function (qlid, asgnid, maxscore, score) {
            var _classAverage = 0;
            if (IsRevel()) {
                return;
            }
            if (knowdldebugMode) debugger;
            var servcUrl = _serviceurl + "/data/econ/common_services/get_class_average/?qlid=" + qlid + "&asgnid=" + asgnid + "&maxscore=" + maxscore + "&score=" + score;
            $.ajax({
                type: "GET",
                async: false,
                url: servcUrl,
                success: function (result) {
                    if (result != undefined && $.trim(result) != "") {
                        _classAverage = Number(result);
                    }
                },
                error: function (error) {
                    _classAverage = 0;
                }
            });

            return _classAverage;
        },
        //Get session data from server
        get_session_data: function () {
            if (IsRevel()) {
                return;
            }
            if (knowdldebugMode) debugger;
            if (typeof g_reachedSummary == 'undefined' || g_reachedSummary == false) {
                var _that = this;
                var servcUrl = _serviceurl + "/gldata/get_session_data/" + TPIData.SessionId + "/";
                $.ajax({
                    type: "GET",
                    url: servcUrl,
                    dataType: "json",
                    async: false,
                    cache: false,
                    success: function (result) {
                        debugger;
                        TPIData.SessionData = JSON.parse(JSON.stringify(result));
                        TPIData.Mode = TPIData.SessionData.launch_data.custom_mode;
                        if (TPIData.Roles != UserRoles.presenter) {
                            TPIData.Roles = TPIData.SessionData.launch_data.roles;
                        }
                        TPIData.CurrentQuestion = TPIData.SessionData.launch_data.custom_currentquestion;
                        TPIData.TargetId = TPIData.SessionData.launch_data['custom_target_' + TPIData.CurrentQuestion];
                        TPIData.ResourceId = TPIData.SessionData.launch_data.custom_resource_id;
                        TPIData.AllowedAttempts = TPIData.SessionData.launch_data.custom_attemptsallowed;
                        TPIData.TargetPoints = TPIData.SessionData.launch_data['custom_points_' + TPIData.CurrentQuestion];

                        var lastAtmtData = undefined;
                        //TPIAttempts = TPIData.SessionData.session_state;

                        if (Utility.getParameterByName("mode", window.location.href) === LaunchMode.review) {
                            TPIData.Mode = LaunchMode.review;
                            var attindx = Number(Utility.getParameterByName("att", window.location.href));
                            lastAtmtData = _that.GetAttemptData(attindx, false); //synchronous get last attempt
                            TPIAttempts = JSON.parse(lastAtmtData.state_data);
                        } else {
                            lastAtmtData = _that.GetLastAttemptData(false); //synchronous get last attempt
                            TPIAttempts = JSON.parse(lastAtmtData.state_data);
                        }

                        //Get Qualsims additional settings
                        _that.getAdditionalSettings();

                        if (TPIAttempts == undefined)
                            TPIAttempts = {};
                        if (TPIAttempts.Attempts == undefined)
                            TPIAttempts.Attempts = [];

                        //att=1&mode=review
                        atmptIndx = TPIAttempts.Attempts.length - 1;


                        if (TPIData.Mode != LaunchMode.review) {
                            if (atmptIndx == -1) {
                                TPIAttempts.Attempts.push($.extend(true, {}, attempt));
                            }
                            atmptIndx = TPIAttempts.Attempts.length - 1;
                        }

                        debugger;
                        if (TPIAttempts.Attempts[atmptIndx].duration)
                            g_TPIDuration = Number(TPIAttempts.Attempts[atmptIndx].duration);

                        if (TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData != undefined) {
                            QLSimModule.SetBookmark(TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData);
                        }
                        //DDeva:31/01/2017 - multiple attempt functionality
                        /*
                                                            if (TPIAttempts.Attempts[TPIAttempts.Attempts.length - 1].reqdData.tempbookmarkData != undefined) {
                                                                tempbookmarkData = TPIAttempts.Attempts[TPIAttempts.Attempts.length - 1].reqdData.tempbookmarkData;
                                                            }
                                                            if (TPIData.Mode === LaunchMode.review && tempbookmarkData) {
                                                                TPIAttempts.Attempts[TPIAttempts.Attempts.length - 1].reqdData.bookmarkData = tempbookmarkData;
                                                            }
                                                            */
                        if (typeof TPIAttempts.Attempts[atmptIndx].requestNo !== "undefined") {
                            g_requestNo = TPIAttempts.Attempts[atmptIndx].requestNo;
                        }

                        if (TPIAttempts.Attempts[atmptIndx].status != "complete") {
                            g_TPIDuration = 0
                            KnowdlTracking.InitLaunch();
                        } else {
                            KnowdlTracking.InitLaunch(true);
                        }

                        if (TPIData.Mode === LaunchMode.do) {
                            if (TPIAttempts.Attempts !== undefined &&
                                atmptIndx >= 0 && (TPIAttempts.Attempts[atmptIndx].lastVisitedPgIndex - 1) > 0) {
                                if (TPIAttempts.Attempts[atmptIndx].lastVisitedPgId != undefined &&
                                    TPIAttempts.Attempts[atmptIndx].lastVisitedPgId != "") {
                                    navlastpage = TPIAttempts.Attempts[atmptIndx].lastVisitedPgId
                                    setTimeout(function () {
                                        GotoPageId(navlastpage);
                                    }, 100);
                                } else {
                                    var nav_splitdata = TPIAttempts.Attempts[0].reqdData.bookmarkData.visitedNodesArray.split(",");
                                    navlastpage = undefined;
                                    for (var spltidx = nav_splitdata.length - 1; spltidx >= 0; spltidx--) {
                                        if ($.trim(nav_splitdata[spltidx]) != "") {
                                            navlastpage = GetPage($.trim(nav_splitdata[spltidx]))
                                            if (navlastpage != undefined) {
                                                navlastpage = $.trim(nav_splitdata[spltidx]);
                                                TPIAttempts.Attempts[atmptIndx].lastVisitedPgId = navlastpage;
                                                break;
                                            }
                                        }
                                    }
                                    if (navlastpage != undefined) {
                                        setTimeout(function () {
                                            GotoPageId(navlastpage);
                                        }, 100);
                                    }
                                }
                            }
                        }

                        skipped_GetSessionData = true;
                        if (g_reachedSummary == true) {
                            g_reachedSummary = true;
                        }

                    },
                    error: function (error) {
                        skipped_GetSessionData = true;
                        if (TPIAttempts == undefined)
                            TPIAttempts = {};
                        if (TPIAttempts.Attempts == undefined) {
                            TPIAttempts.Attempts = [];
                            TPIAttempts.Attempts.push($.extend(true, {}, attempt))
                        }

                    }
                });
            }
        },
        // save session data
        SaveSessionData: function (isRetrieve, asyncParam, closecallback) {
            if (IsRevel()) {
                SetRevelStateData();
                if ((gPages[0].PageId + "") != (gCurrPageObj.PageId + "")) {
                    if (k_Revel.get_LaunchData().mode == LaunchModes.do) {
                        var r_locdata = k_Revel.get_LocalData();
                        if (r_locdata != undefined && r_locdata.CompletionStatus != "complete") {
                            var percScore = QLSimModule.GetTotalScore();
                            k_Revel.PostData(Number(percScore), (Number(percScore) / 100), true);
                        }
                    }
                }
                return;
            }
            if (TPIData.Mode.trim().toLowerCase() != LaunchMode.review) {
                //TPIAttempts.Attempts[atmptIndx].no = atmptIndx + 1; //no use
                if (TPIAttempts.Attempts[atmptIndx].status != "complete") {
                    TPIAttempts.Attempts[atmptIndx].status = "inprogress";
                }
                TPIAttempts.Attempts[atmptIndx].duration = parseInt((new Date().getTime() - _startTime.getTime()) / 1000) + g_TPIDuration;
                var overallScore = QLSimModule.GetTotalScore();
                TPIAttempts.Attempts[atmptIndx].overallScore = overallScore;
                //DDeva: 29Mar17 - redirect to last page
                if (!(TPIAttempts.Attempts[atmptIndx].status == "complete" && gCurrPageObj.PageId == moduleStartPage)) {
                    TPIAttempts.Attempts[atmptIndx].lastVisitedPgIndex = gCurrPageObj.ArrayIndex + 1;
                    TPIAttempts.Attempts[atmptIndx].lastVisitedPgId = gCurrPageObj.PageId;
                }

                if (isRetrieve) {
                    //save the current attempt data into temp and make the current attempt empty
                    //DDeva:31/01/2017_ - multiple attempt functionality
                    var tempbookmarkData = $.extend(true, {}, QLSimModule.GetBookmark());
                    tempbookmarkData.overallScore = overallScore;
                    tempbookmarkData.currentAttempt--;
                    TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData = tempbookmarkData;
                    if (TPIAttempts.Attempts[atmptIndx].maxscore < overallScore) {
                        TPIAttempts.Attempts[atmptIndx].maxscore = overallScore;
                    }
                    var _prevMaxScore = TPIAttempts.Attempts[atmptIndx].maxscore;
                    TPIAttempts.Attempts[atmptIndx].requestNo = g_requestNo++;
                    //nav - earlier it was in InitAttemptData taken outside for preview mode. 
                    QLSimModule.Reset();
                    TPIAttempts.Attempts = [];
                    TPIAttempts.Attempts.push($.extend(true, {}, attempt));
                    if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do && TPIAttempts.Attempts[TPIAttempts.Attempts.length - 1].status == 'new') {
                        if (TPIAttempts.Attempts[atmptIndx].maxscore < _prevMaxScore) {
                            TPIAttempts.Attempts[atmptIndx].maxscore = _prevMaxScore;
                        }
                    }
                    //end
                    this.InitAttemptData();
                    atmptIndx = TPIAttempts.Attempts.length - 1;
                } else {
                    TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData = QLSimModule.GetBookmark();
                    TPIAttempts.Attempts[atmptIndx].requestNo = g_requestNo++;
                    this.SaveAttempData(asyncParam, closecallback);
                }
            }
        },
        GetLastAttemptData: function (asyncStatus) {
            if (IsRevel()) {
                return;
            }
            //if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
            var servcUrl = _serviceurl + "/data/econ/common_services/get_qlsim_lastattempt_data/?sessionId=" + TPIData.SessionId;
            $.fancybox.showActivity();
            var outResult;
            $.ajax({
                type: "GET",
                url: servcUrl,
                async: asyncStatus,
                success: function (result) {
                    //var localobj = JSON.stringify(result);
                    //Data posted successfully
                    $.fancybox.hideActivity();
                    outResult = result;
                },
                error: function (error) {
                    $.fancybox.hideActivity();
                }
            });
            return outResult;
            //}
        },
        //NM - Get users attempt count, status can be configured, for now it is hardcoded to 'complete'
        GetUserAttemptCount: function (asyncStatus) {
            if (IsRevel()) {
                return;
            }
            /*http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_attempt_count/?sessionId=[sessionId]&status=complete */
            var servcUrl = _serviceurl + "/data/econ/common_services/get_qlsim_attempt_count/?sessionId=" + TPIData.SessionId + "&status=complete";
            $.fancybox.showActivity();
            var outResult;
            $.ajax({
                type: "GET",
                url: servcUrl,
                async: asyncStatus,
                success: function (result) {
                    //var localobj = JSON.stringify(result);
                    //Data posted successfully
                    $.fancybox.hideActivity();
                    outResult = result;
                },
                error: function (error) {
                    $.fancybox.hideActivity();
                }
            });
            return outResult;
        },

        //DDeva:07/02/2017 - initializing attempt code
        InitAttemptData: function () {
            if (IsRevel()) {
                return;
            }
            if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                var jsonSerialized = JSON.stringify({
                    'sessionId': TPIData.SessionId,
                    'jsonData': TPIAttempts
                });
                //replace special characters.
                jsonSerialized = jsonSerialized.replace(/[^a-zA-Z ',"<>!~@#$%&*.+-=|\?()\[\]_{}\\ ]/g, "");
                var servcUrl = _serviceurl + "/data/econ/common_services/init_qlsim_attempt_data/";
                $.fancybox.showActivity();
                $.ajax({
                    type: "POST",
                    url: servcUrl,
                    data: jsonSerialized,
                    async: false,
                    success: function (result) {
                        //var localobj = JSON.stringify(result);
                        //Data posted successfully
                        $.fancybox.hideActivity();
                    },
                    error: function (error) {
                        $.fancybox.hideActivity();
                    }
                });
            }
        },
        // Send session data to server
        SaveAttempData: function (asyncParam, closecallback) {
            if (IsRevel()) {
                return;
            }
            if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                asyncParam = typeof asyncParam == 'undefined' ? true : asyncParam;
                var jsonSerialized = JSON.stringify({
                    'sessionId': TPIData.SessionId,
                    'jsonData': TPIAttempts
                });
                //replace special characters.
                jsonSerialized = jsonSerialized.replace(/[^a-zA-Z ',"<>!~@#$%&*.+-=|\?()\[\]_{}\\ ]/g, "");
                var servcUrl = _serviceurl + "/data/econ/common_services/save_qlsim_attempt_data/";

                if (typeof closecallback !== 'undefined') {
                    $.fancybox.showActivity();
                    $.ajax({
                        async: asyncParam,
                        type: "POST",
                        url: servcUrl,
                        data: jsonSerialized,
                        success: function (result) {
                            //var localobj = JSON.stringify(result);
                            //Data posted successfully
                            $.fancybox.hideActivity();
                            window.close();
                        },
                        error: function (error) {
                            $.fancybox.hideActivity();
                            window.close();
                        }
                    });
                } else {
                    if (!asyncParam) {
                        $.fancybox({
                            content: "<div id='savingdatapopupmsg' tabindex='1' role='alert'  class='Open-Sans-Font-16px' style='padding:15px;background-color:#ffffff;'>Saving data...</div>",
                            modal: true,
                            'onComplete': function () {
                                $("div:visible").removeAttr("aria-hidden");
                                setTimeout(function () {
                                    $("#savingdatapopupmsg").focus();
                                }, 0);
                            },
                            'onClosed': function () {
                                setTimeout(function () {
                                    if ($(".ui-dialog").length > 0) {
                                        $("#dialog").attr("role", "alert");
                                        $("#dialog").attr("tabindex", "1");
                                        setTimeout(function () {
                                            $("#dialog").focus();
                                        }, 100);
                                    } else {
                                        $(".CaseTitle").focus();
                                    }
                                }, 200);
                            }
                        });
                    }
                    $.ajax({
                        async: true,
                        type: "POST",
                        url: servcUrl,
                        data: jsonSerialized,
                        success: function (result) {
                            //var localobj = JSON.stringify(result);
                            //Data posted successfully
                            //$.fancybox.hideActivity(); 
                            if (!asyncParam) {
                                $.fancybox.close();
                                setTimeout(function () {
                                    if ($("#fancybox-content") != undefined && $("#fancybox-content") != null) {
                                        if ($("#fancybox-content").text().toLowerCase() == 'saving data...') {
                                            $.fancybox.close();
                                        }
                                    }
                                }, 5000)
                            }

                        },
                        error: function (error) {
                            //$.fancybox.hideActivity(); 
                            if (!asyncParam) {
                                $.fancybox.close();
                                setTimeout(function () {
                                    if ($("#fancybox-content") != undefined && $("#fancybox-content") != null) {
                                        if ($("#fancybox-content").text().toLowerCase() == 'saving data...') {
                                            $.fancybox.close();
                                        }
                                    }
                                }, 5000)
                            }
                        }
                    });
                }
            }
        },
        // Get particular attempt data for review mode
        GetAttemptData: function (_atmtNo, asyncStatus) {
            if (IsRevel()) {
                return;
            }
            if (TPIData.Mode.trim().toLowerCase() == LaunchMode.review) {
                if (typeof _atmtNo == 'undefined') {
                    _atmtNo = 0;
                }
                var outResult;
                var servcUrl = _serviceurl + "/data/econ/common_services/get_qlsim_attempt_data/?sessionId=" + TPIData.SessionId + "&attIndex=" + _atmtNo;
                $.ajax({
                    type: "GET",
                    url: servcUrl,
                    dataType: "json",
                    async: asyncStatus,
                    cache: false,
                    success: function (result) {
                        outResult = result;
                        //var localobj = JSON.parse(result);
                        //Data posted successfully
                    },
                    error: function (error) {}
                });
                return outResult;
            }
        },
        // Save completion mark
        TPICompletionMark: function (userTotalScore, callback) {
            if (knowdldebugMode) debugger;
            if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                var seconds = parseInt((new Date().getTime() - _startTime.getTime()) / 1000);

                var studentdata = {};
                studentdata.score = (Number(userTotalScore) * Number(TPIData.TargetPoints)).toFixed(2);
                studentdata.duration = seconds + g_TPIDuration;
                studentdata.submissionCount = TPIAttempts.Attempts.length;
                studentdata.nAttempts = TPIAttempts.Attempts.length;
                studentdata.answers = "1";
                studentdata.problemNumber = TPIData.CurrentQuestion;

                //grade_problem_and_reportjs(studentdata, true)
                //target id here containd backslash and so url mapping may not work 
                //sending placeholder for "target id" and replace it with "target id" from launch data in python code
                this.grade_problem_and_report(studentdata, TPIData.SessionId, 'usefromsession');

                if (typeof callback !== 'undefined') {
                    callback();
                }
            }
        },
        //Send data to server for completion marking
        grade_problem_and_report: function (sampleObject, sid, p_gid) {
            if (IsRevel()) {
                return;
            }
            if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do) {
                var jsonSerialized = JSON.stringify(sampleObject);
                var servcUrl = _serviceurl + "/gldata/grade_problem_and_report/" + sid + "/" + p_gid + "/";
                $.ajax({
                    type: "POST",
                    url: servcUrl,
                    data: jsonSerialized,
                    success: function (result) {
                        //var localobj = JSON.parse(result);
                        //Data posted successfully
                    },
                    error: function (error) {}
                });
            }
        },
        //Get Qualsims additional settings 
        getAdditionalSettings: function () {
            if (IsRevel()) {
                return;
            }
            if (TPIData.Mode.trim().toLowerCase() == LaunchMode.do || TPIData.Mode.trim().toLowerCase() == LaunchMode.review) {
                var obj = {};
                obj.knowdlresourceid = TPIData.ResourceId;
                obj.knowdltargetapp = TPIData.TargetId;

                var jsonSerialized = JSON.stringify(obj);
                var servcUrl = _serviceurl + "/data/econ/inflation/getInflationSettings/";
                $.ajax({
                    type: "POST",
                    url: servcUrl,
                    async: false,
                    data: jsonSerialized,
                    success: function (result) {
                        KnowdlTracking.set_Settings(result);
                    },
                    error: function (error) {

                    }
                });
            }
        }

    };
})();


//Call below function on k_Cust_OnOrientationChange() and k_Cust_LoadPageContentComplete()
//QLOptionRandomizer.Init();
//end Call
if (typeof (isModuleLoaded) === 'undefined') {
    var QLOptionRandomizer = (function () {
        var isHAlignment = false;
        var OptionSpacing = 20;
        var StartTop = 0;
        var StartLeft = 0;
        var RandomState = [];

        var QLOptions = [];

        var QLSkipRandomization = [182]

        //Private function definitions goes here
        function _privateFunction(param1, param2) {}
        //end private functions
        //Public function definitions goes here  
        return {
            ResetRandomState: function () {
                RandomState = [];
            },
            GetRandomState: function () {
                return RandomState;
            },
            SetRandomState: function (_randomState) {
                //Deva 17Feb16 to check for undefined
                if (typeof _randomState === 'undefined') {
                    _randomState = [];
                }
                RandomState = _randomState;
            },
            Init: function () {
                if (this.IsSkipRandomization(gCurrPageObj.PageId)) {
                    return;
                }
                QLOptions = $(".k-element-box[temptype='Button'][simscore]:visible");
                isHAlignment = false;
                if (QLOptions.length > 1) {
                    QLOptions.sort(function (obj1, obj2) {
                        // Ascending: 
                        return $(obj1).position().top - $(obj2).position().top;
                        //Descending
                        //return $(obj2).position().top - $(obj1).position().top;
                    });

                    var tabIndexes = [];
                    for (var i = 0; i < QLOptions.length; i++) {
                        tabIndexes.push(Number($(QLOptions[i]).attr('tabindex')));
                    }
                    tabIndexes.sort(function (a, b) {
                        return a - b
                    });

                    var tdiff = $(QLOptions[1]).position().top - $(QLOptions[0]).position().top;
                    if (tdiff < 30) {
                        QLOptions.sort(function (obj1, obj2) {
                            return $(obj1).position().left - $(obj2).position().left;
                        });
                        isHAlignment = true;
                        OptionSpacing = $(QLOptions[1]).position().left - ($(QLOptions[0]).position().left + $(QLOptions[0]).width());
                    } else {
                        OptionSpacing = $(QLOptions[1]).position().top - ($(QLOptions[0]).position().top + $(QLOptions[0]).height());
                    }

                    StartTop = $(QLOptions[0]).position().top;
                    StartLeft = $(QLOptions[0]).position().left;

                    var rstate = this.GetRState(gCurrPageObj.PageId),
                        mode = '';
                    if (rstate == undefined) {
                        if (rstate == undefined) {
                            rstate = {};
                        }
                        rstate.PageId = gCurrPageObj.PageId;
                        rstate.OptionIds = [];

                        QLOptions = Utility.shuffle(QLOptions)
                        for (var i = 0; i < QLOptions.length; i++) {
                            $(QLOptions[i]).find('.div-edit-properties').attr('tabindex', tabIndexes[i]);
                            rstate.OptionIds.push($(QLOptions[i]).find(".k-element-button").attr("id"));
                        }

                        RandomState.push(rstate);
                    } else {
                        mode = 'review';
                    }
                    var extraParams = {};
                    extraParams.isHAlignment = isHAlignment;
                    extraParams.StartTop = StartTop;
                    extraParams.StartLeft = StartLeft;
                    extraParams.OptionSpacing = OptionSpacing;
                    this.Randomize(rstate, extraParams, tabIndexes, mode);
                    UpdateDOMElementSequence();
                }
            },
            Randomize: function (_rState, _extraParams, tabIndexes, mode) {
                if (_rState != undefined) {
                    if (_extraParams.isHAlignment) {
                        var pos = _extraParams.StartLeft;
                        for (var i = 0; i < _rState.OptionIds.length; i++) {
                            $("#" + _rState.OptionIds[i]).closest(".k-element-box").css({
                                "left": pos
                            });
                            pos = pos + $("#" + _rState.OptionIds[i]).closest(".k-element-box").width() + _extraParams.OptionSpacing;
                        }

                    } else {
                        var pos = _extraParams.StartTop;
                        for (var i = 0; i < _rState.OptionIds.length; i++) {
                            var tempCheckListId = $("#" + _rState.OptionIds[i]).closest(".k-element-box").attr("relChecklistID");
                            var $optn = $("#" + _rState.OptionIds[i]);
                            $optn.closest(".k-element-box").css({
                                "top": pos
                            });
                            /*if (mode == 'review') {
                                            //updated for randomization issue fix
                                            $optn.closest(".k-element-box").attr('tabindex', tabIndexes[i]);
                                            $optn.removeAttr('tabindex');
                                          } else {*/
                            $optn.closest(".k-element-box").attr('tabindex', tabIndexes[i]);
                            $optn.removeAttr('tabindex');
                            //}
                            if (tempCheckListId != undefined || tempCheckListId != '') {
                                $("#" + tempCheckListId).closest(".k-element-box").css({
                                    "top": pos
                                });
                                $("#" + tempCheckListId).find("input[type='checkbox']").attr('tabindex', tabIndexes[i]);
                            }
                            pos = pos + $optn.closest(".k-element-box").height() + _extraParams.OptionSpacing;
                        }
                    }
                }
            },
            GetRState: function (_pageId) {
                var rst = undefined;
                for (var j = 0; j < RandomState.length; j++) {
                    if (RandomState[j].PageId == _pageId) {
                        if (typeof QLSimModule.GetVisitedPage(gCurrPageObj.PageId) === 'undefined') {
                            RandomState.splice(j, 1);
                        }
                        rst = RandomState[j];
                        break;
                    }
                }
                return rst;
            },

            IsSkipRandomization: function (_pageId) {
                var isSkip = false;
                for (var j = 0; j < QLSkipRandomization.length; j++) {
                    if ((QLSkipRandomization[j] + "") == (_pageId + "")) {
                        isSkip = true;
                        break;
                    }
                }
                return isSkip;
            }
        };
        //end public functions
    })();

    var CustomizeComponents = (function () {
        var SkipPageArray = [182]
        return {
            ApplyWrapperToButtonImg: function (_optionId) {
                if (this.IsSkipPage(gCurrPageObj.PageId)) {
                    return;
                }
                if (_optionId == undefined) {
                    //$("span.btnImgWrapper").remove();
                    var _QLOptions = $(".k-element-box[temptype='Button'][simscore]:visible");
                    if (_QLOptions.length > 1) {
                        for (var i = 0; i < _QLOptions.length; i++) {
                            var imgObj = $(_QLOptions[i]).find("img.lblImg:visible");
                            if (imgObj.length > 0) {
                                var imgwrapper = "<span class='btnImgWrapper' style='float:left;'>" + imgObj.get(0).outerHTML + "</span>";
                                if (imgObj.closest("span.btnImgWrapper").length <= 0) {
                                    imgObj.replaceWith(imgwrapper);
                                }
                            }
                        }
                    }
                }
            },
            IsSkipPage: function (_pageId) {
                var isSkip = false;
                for (var j = 0; j < SkipPageArray.length; j++) {
                    if ((SkipPageArray[j] + "") == (_pageId + "")) {
                        isSkip = true;
                        break;
                    }
                }
                return isSkip;
            }
        };
    })();
}

//Usage: 
//CustomizeComponents.ApplyWrapperToButtonImg()
//QLOptionRandomizer.Init();

function UpdateDOMElementSequence() {
    debugger;
    // update position according to randomization for arrow key navigation
    $(".column").find(".k-element-box[simscore][temptype='Checklist']").removeAttr("simscore");
    var tempelmlist = $(".column").find(".k-element-box[simscore]");
    var fep = tempelmlist.first().prev();
    while (fep.get(0).getAttribute("temptype") != 'Text' && fep.get(0).getAttribute("temptype") != 'TextAsset') {
        fep = fep.prev();
    }
    tempelmlist.sort(function (a, b) {
        var numericallyOrderedDivs = $(".column").find(".k-element-box[simscore]").sort(function (a, b) {
            return a.getAttribute('tabindex') - b.getAttribute('tabindex');
        });
        fep.after(numericallyOrderedDivs);
    });
    var tempchkelmlist = $(".column").find(".k-element-box.optionelement[temptype='Checklist']");
    if (tempchkelmlist.length > 0) {
        tempchkelmlist.sort(function (a, b) {
            var numericallyOrderedcheckDivs = $(".column").find(".k-element-box.optionelement[temptype='Checklist']").sort(function (a, b) {
                return $(a).find("input[type='checkbox']").get(0).getAttribute('tabindex') - $(b).find("input[type='checkbox']").get(0).getAttribute('tabindex');
            });

            fep.after(numericallyOrderedcheckDivs);
        });
        //NM- Code to handle tabindex in review mode for CheckList Options.
        for (var i = 0; i < tempchkelmlist.length; i++) {
            if ($(tempchkelmlist[i]).find("input[type='checkbox']").get(0).hasAttribute("disabled")) {
                var tindx = $(tempchkelmlist[i]).find("input[type='checkbox']").attr("tabindex")
                $(tempchkelmlist[i]).find("input[type='checkbox']").closest("tr").attr("tabindex", tindx);
            }
        }
        //End
        if ((/Edge/.test(navigator.userAgent)) || (isIE11version == true)) {
            $(".column").find(".k-element-box[simscore]").removeAttr("tabindex");
        } else {
            $(".column").find(".k-element-box[simscore]").removeAttr("tabindex");
            //setTimeout(function () { $(".column").find(".k-element-box[simscore]").removeAttr("tabindex").attr("aria-hidden", true); }, 100);
        }
    }
}

function InitFromRevelStateData(r_statedata) {
    TPIData.Mode = k_Revel.get_LaunchData().mode;
    TPIData.AllowedAttempts = k_Revel.get_Settings().AllowedAttempts;
    TPIData.TargetPoints = k_Revel.get_Settings().TargetPoints;

    TPIAttempts = r_statedata;

    if (TPIAttempts == undefined)
        TPIAttempts = {};
    if (TPIAttempts.Attempts == undefined)
        TPIAttempts.Attempts = [];

    //att=1&mode=review
    atmptIndx = TPIAttempts.Attempts.length - 1;
    if (TPIData.Mode != LaunchMode.review) {
        if (atmptIndx == -1) {
            TPIAttempts.Attempts.push($.extend(true, {}, attempt));
        }
        atmptIndx = TPIAttempts.Attempts.length - 1;
    }

    if (TPIAttempts.Attempts[atmptIndx].duration)
        g_TPIDuration = Number(TPIAttempts.Attempts[atmptIndx].duration);

    if (TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData != undefined) {
        QLSimModule.SetBookmark(TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData);
    }

    if (typeof TPIAttempts.Attempts[atmptIndx].requestNo !== "undefined") {
        g_requestNo = TPIAttempts.Attempts[atmptIndx].requestNo;
    }

    if (TPIAttempts.Attempts[atmptIndx].status != "complete") {
        g_TPIDuration = 0
    }
    //NM:21-July-2017 - bookmark page logic is changed from page index to page Id.
    //We are not removing lastVisitedPgIndex prop but will not use it.
    //will use newly added lastVisitedPgId prop.
    if (TPIData.Mode === LaunchMode.do) {
        if (TPIAttempts.Attempts !== undefined &&
            atmptIndx >= 0 && (TPIAttempts.Attempts[atmptIndx].lastVisitedPgIndex - 1) > 0) {
            if (TPIAttempts.Attempts[atmptIndx].lastVisitedPgId != undefined && TPIAttempts.Attempts[atmptIndx].lastVisitedPgId != "") {
                navlastpage = TPIAttempts.Attempts[atmptIndx].lastVisitedPgId
                setTimeout(function () {
                    GotoPageId(navlastpage);
                }, 100);
            } else {
                var nav_splitdata = TPIAttempts.Attempts[0].reqdData.bookmarkData.visitedNodesArray.split(",");
                navlastpage = undefined;
                for (var spltidx = nav_splitdata.length - 1; spltidx >= 0; spltidx--) {
                    if ($.trim(nav_splitdata[spltidx]) != "") {
                        navlastpage = GetPage($.trim(nav_splitdata[spltidx]))
                        if (navlastpage != undefined) {
                            navlastpage = $.trim(nav_splitdata[spltidx]);
                            TPIAttempts.Attempts[atmptIndx].lastVisitedPgId = navlastpage;
                            break;
                        }
                    }
                }
                if (navlastpage != undefined) {
                    setTimeout(function () {
                        GotoPageId(navlastpage);
                    }, 100);
                }
            }
        }
    }

    skipped_GetSessionData = true;
    if (g_reachedSummary == true) {
        g_reachedSummary = true;
    }

}

function SetRevelStateData() {
    if (IsRevel()) {
        if ((gPages[0].PageId + "") != (gCurrPageObj.PageId + "")) {
            if (k_Revel.get_LaunchData().mode == LaunchModes.do) {
                //TPIAttempts.Attempts[atmptIndx].no = atmptIndx + 1; //no use
                if (TPIAttempts.Attempts[atmptIndx].status != "complete") {
                    TPIAttempts.Attempts[atmptIndx].status = "inprogress";
                }
                TPIAttempts.Attempts[atmptIndx].duration = parseInt((new Date().getTime() - _startTime.getTime()) / 1000) + g_TPIDuration;
                var overallScore = QLSimModule.GetTotalScore();
                TPIAttempts.Attempts[atmptIndx].overallScore = overallScore;
                //DDeva: 29Mar17 - redirect to last page
                if (gCurrPageObj.PageId != gPages[0]) {
                    TPIAttempts.Attempts[atmptIndx].lastVisitedPgIndex = gCurrPageObj.ArrayIndex + 1;
                    //NM:21-July-2017 - bookmark page logic is changed from page index to page Id.                    
                    TPIAttempts.Attempts[atmptIndx].lastVisitedPgId = gCurrPageObj.PageId;
                }

                TPIAttempts.Attempts[atmptIndx].reqdData.bookmarkData = QLSimModule.GetBookmark();
                TPIAttempts.Attempts[atmptIndx].requestNo = g_requestNo++;


                k_Revel.set_StateData(TPIAttempts)
            }
        }
    }
}