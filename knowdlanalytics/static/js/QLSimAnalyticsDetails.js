$(document).ready(function () {
	debugger
	if ($("#selectedLOC").length > 0) {
    	$("#selectedLOC").change();
    }
	var qsparam = Utility.getParameterByName("Course_Id", document.location.href)
	if(qsparam != undefined && qsparam!=""){
		$("#analyticsHeader").hide()
	}	
	$(".asgnTitle").html(document.getElementById("selectedASGN").options[document.getElementById("selectedASGN").selectedIndex].text);
    $(".ql .tabs a.reporttab[rel='Overview']").click();
});

var Utility = function () { return { shuffle: function (e) { for (var t, n, r = e.length; 0 !== r;) n = Math.floor(Math.random() * r), r -= 1, t = e[r], e[r] = e[n], e[n] = t; return e }, getParameterByName: function (e, t) { e = e.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]"); var n = new RegExp("[\\?&]" + e + "=([^&#]*)"), r = n.exec(t); return null === r ? "" : decodeURIComponent(r[1].replace(/\+/g, " ")) }, updateHtml: function (e, t) { $.each(e, function (e, n) { var r = "", a = $(n); $.each(t, function (e, t) { var n = new RegExp(e, "g"); r += a.html().replace(n, t) }), a.html(r) }) }, mergeArray: function (e, t) { var n = e.concat(t).sort(function (e, t) { return e > t ? 1 : t > e ? -1 : 0 }); return n.filter(function (e, t) { return n.indexOf(e) === t }) }, injectCss: function (e) { var t = document.getElementsByTagName("head")[0], n = document.createElement("style"); n.setAttribute("type", "text/css"), n.styleSheet ? n.styleSheet.cssText = e : n.appendChild(document.createTextNode(e)), t.appendChild(n) }, getRandomIntInclusive: function (e, t) { return Math.floor(Math.random() * (t - e + 1)) + e }, getAbbrNum: function (e, t, n, r) { if (0 > e) var a = -1; else var a = 1; -1 == a ? (a = "-", e = Math.abs(e)) : a = "", t = Math.pow(10, t); for (var o = ["k", "m", "b", "t"], c = o.length - 1; c >= 0; c--) { var u = Math.pow(10, 3 * (c + 1)); if (e >= u) { e = Math.round(e * t / u) / t, 1e3 == e && c < o.length - 1 && (e = 1, c++), e += o[c]; break } } return a + n + e } } }();
var gQLId = "";
var gCourse_Id = "";
var gASGN = "";

var _graphVars = {
        "graphBand": "<div style='position:relative;left:0px;' id='graphBand'></div>",
        "graphDivForPie": "<div id='forPieChartA' tabindex='7' style='position: absolute;top: 15px;left: 20px;height: 260px;width: 260px;'></div><div id='forPieChartB' tabindex='8' style='position: absolute;top: 48px;left: 280px;height: 240px;width: 240px;'></div>",
        "graphDivForBar": "<div id='forBarChart' tabindex='7' style='position: absolute;top: 15px;left: 20px;height: 300px;width: 100%;'></div>",
        "resultsDiv": "<div style='position:absolute;left:0px;top:395px;width:740px;' id='resultsDiv'></div>",
        "pieALabel": '<div id="pieALabel" style="position: absolute;top: 113px;left: 75px;color:#007fa2;font-size: 50px;font-family: \'Open Sans\';width:128px;text-align:center;"></div>',
        "pieBLabel": '<div id="pieBLabel" style="position: absolute;top: 141px;left: 348px;color:#007fa2;font-size: 40px;font-family: \'Open Sans\';width:102px;text-align:center;"></div>'
    }

function SetParameters(){
    gQLId = $("#selectedSim").val();
    gCourse_Id = $("#selectedLOC").val();
    gASGN = $("#selectedASGN").val();
    if (gQLId == undefined || gQLId == "") {
        gQLId = Utility.getParameterByName("QL_Id", document.location.href);
    }
    if (gCourse_Id == undefined || gCourse_Id == "") {
        gCourse_Id = Utility.getParameterByName("Course_Id", document.location.href);
    }
    if (gASGN == undefined || gASGN == "") {
        gASGN = Utility.getParameterByName("ASGN", document.location.href);                
    }
}

$(".ql .tabs a.reporttab").live("click", function () {
    var rel = $(this).attr("rel");
    $(".ql .title .sub .tabname").html(rel);
    //show tab link.
    $(".ql .tabs a.reporttab").removeClass("selected");
    $(this).addClass("selected");

    //show tab.
    $(".ql .analyticsResult .tabContainer").addClass("hide");
    $(".ql .analyticsResult .tabContainer[rel='" + rel + "']").removeClass("hide");


    switch (rel) {
        case "Overview":
            GetOverviewDetails();
            break;
        case "Class":
            GetClassReportDetails();
            break;
        case "Student":
            GetStudentDetails();
            break;
        case "Outcomes":
            ShowOutcomes();
            break;
    }
    if ($(".expandcollapse").hasClass("collapse")) {
        expand(rel);               
    }
    else {
        collapse(rel);
    }
});


function GetOverviewDetails() {
    if ($(".tabContainer[rel='Overview']").find("table").length <= 0) {
        SetParameters();
        //var _data = { "QL_Id": gQLId, "Course_Id": gCourse_Id, "ASGN": gASGN };
        var servcUrl = "/knowdlanalytics/QLSimOverview/?Course_Id=" + gCourse_Id + "&ASGN=" + gASGN + "&QL_Id=" + gQLId;
        $.ajax({
            type: "GET",
            async: false,
            url: servcUrl,            
            success: function (result) {
                $(".tabContainer[rel='Overview']").html(result);                        
                $(".questionOverviewDetailsRow").hide();
                var pfirst = Number($("#hiddenOverviewAvgGrade").val());
                var psecond = Number($("#hiddenOverviewCompleted").val());
                _graphUtility.initialiseGraph(pfirst, psecond, "pie","overview");
            },
            error: function (error) {

            }
        });
    } else {
        var pfirst = Number($("#hiddenOverviewAvgGrade").val());
        var psecond = Number($("#hiddenOverviewCompleted").val());
        _graphUtility.initialiseGraph(pfirst, psecond, "pie", "overview");
    }
}

function GetClassReportDetails() {
    if ($(".tabContainer[rel='Class']").find("table").length <= 0) {
        SetParameters();
        //var _data = { "QL_Id": gQLId, "LOC": gCourse_Id, "ASGN": gASGN };
        var servcUrl = "/knowdlanalytics/QLSimClassReport/?Course_Id=" + gCourse_Id + "&ASGN=" + gASGN + "&QL_Id=" + gQLId;
        $.ajax({
            type: "GET",
            async: false,
            url: servcUrl,            
            success: function (result) {
                $(".tabContainer[rel='Class']").html(result);                        
                $(".questionOverviewDetailsRow").hide();
                var pfirst = Number($("#hiddenClassReportAvgGrade").val());
                var psecond = Number($("#hiddenClassReportMedian").val());
                _graphUtility.initialiseGraph(pfirst, psecond, "pie", "class")
            },
            error: function (error) {

            }
        });
    } else {
        var pfirst = Number($("#hiddenClassReportAvgGrade").val());
        var psecond = Number($("#hiddenClassReportMedian").val());
        _graphUtility.initialiseGraph(pfirst, psecond, "pie", "class")
    }
}

function GetStudentDetails() {
    var _studentName = "";
    if ($(".tabContainer[rel='Student']").find("table").length <= 0) {
        SetParameters();
        //var _data = { "QL_Id": gQLId, "LOC": gCourse_Id, "ASGN": gASGN };
        var servcUrl = "/knowdlanalytics/QLSimStudentReport/?Course_Id=" + gCourse_Id + "&ASGN=" + gASGN + "&QL_Id=" + gQLId;
        $.ajax({
            type: "GET",
            async: false,
            url: servcUrl,            
            success: function (result) {
                $(".tabContainer[rel='Student']").html(result);
                $(".tabContainer[rel='Student']").find(".studentDetailRow").hide();                        
                $(".tabContainer[rel='Student']").find("span").css({ "font-size": "14px" });
                $(".tabContainer[rel='Student'] .FeedbackDiv").find("p:contains('Click'):contains('Next'):contains('to'):contains('continue')").remove();
                $(".tabContainer[rel='Student'] .FeedbackDiv").find("em:contains('Click'):contains('Next'):contains('to'):contains('continue')").closest("p").remove();
                $(".studentDetailQuestionRow").hide();
                var psecond = parseInt($(".tabContainer[rel='Student']").find("#hiddenClassReportAvgGrade").val());
                _graphUtility.initialiseGraph(0, psecond, "pie", "student", "");

            },
            error: function (error) {

            }
        });
    } else {
        var psecond = parseInt($(".tabContainer[rel='Student']").find("#hiddenClassReportAvgGrade").val());
        _graphUtility.initialiseGraph(0, psecond, "pie", "student", _studentName);

    }
}

function expand(rel) {

    switch (rel) {
        case "Overview":
            $(".ql .analyticsResult .tabContainer[rel='" + rel + "']").find(".questionOverviewRow").addClass("optionsDisplayed");
            $("tr.questionOverviewDetailsRow").show();
            break;
        case "Class":
            $(".ql .analyticsResult .tabContainer[rel='" + rel + "']").find(".questionOverviewRow").addClass("optionsDisplayed");
            $("tr.questionOverviewDetailsRow").show();
            break;
        case "Student":
            $(".ql .analyticsResult .tabContainer[rel='" + rel + "']").find("tr.studentRow").show();
            $("tr.studentRow").addClass("studentDisplayed");
            $("tr.studentDetailRow").show();
            $("tr.studentDetailRow").addClass("questionDisplayed");
            $("tr.studentDetailQuestionRow").show();
            break;
        case "Outcomes":

            break;
    }

}
function collapse(rel)
{
    switch (rel) {
        case "Overview":
            $(".ql .analyticsResult .tabContainer[rel='" + rel + "']").find(".questionOverviewRow").removeClass("optionsDisplayed");
            $("tr.questionOverviewDetailsRow").hide();
            break;
        case "Class":
            $(".ql .analyticsResult .tabContainer[rel='" + rel + "']").find(".questionOverviewRow").removeClass("optionsDisplayed");
            $("tr.questionOverviewDetailsRow").hide();
            break;
        case "Student":
            $("tr.studentRow").removeClass("studentDisplayed");
            $("tr.studentDetailRow").hide();
            $("tr.studentDetailRow").removeClass("questionDisplayed");
            $("tr.studentDetailQuestionRow").hide();
            break;
        case "Outcomes":

            break;
    }
}

$(".ql .tabs a.expand").live("click", function () {
    //debugger;
    var rel = $(".ql .tabs a.reporttab.selected").attr("rel");
    expand(rel);
    $(this).addClass("collapse");
    $(this).removeClass("expand");
});

$(".ql .tabs a.collapse").live("click", function () {

    var rel = $(".ql .tabs a.reporttab.selected").attr("rel");
    collapse(rel);
    $(this).removeClass("collapse");
    $(this).addClass("expand");
});

$(".questionOverviewRow").live("click", function () {
    debugger;
    var qsnId = $(this).attr("data-questionid");
    if ($(this).hasClass("optionsDisplayed")) {
        $(this).removeClass("optionsDisplayed");
        $("tr.questionOverviewDetailsRow[data-questionid ='" + qsnId + "']").hide();
    }
    else {
        $(this).addClass("optionsDisplayed");
        $("tr.questionOverviewDetailsRow[data-questionid ='" + qsnId + "']").show();
    }
    event.stopPropagation();
    
});

var _graphUtility = (function () {
    return {
        initialiseGraph: function (_leftPerc, _rightPerc, _type, _section, _additionalData) {
            _leftPerc = Number(Number(_leftPerc).toFixed("0"));
            _rightPerc = Number(Number(_rightPerc).toFixed("0"));
            debugger
            if (Highcharts.charts != undefined && Highcharts.charts.length > 0) {
                for (var i = 0; i < Highcharts.charts.length; i++) {
                    if (Highcharts.charts[i] != undefined) {
                        Highcharts.charts[i].destroy();
                    }
                }
                Highcharts.charts.splice(0, Highcharts.charts.length)
            };

            $('#forPieChartA').remove();
            $('#forPieChartB').remove();
            $('#pieALabel').remove();
            $('#pieBLabel').remove();
            $('#forBarChart').remove();
            $("#graphBand").remove();

            $(".charts").append(_graphVars.graphBand);

            var _graphTitleA = "";
            var _graphTitleB = "";

            switch (_section) {
                case "overview":
                    _graphTitleA = "Average Grade";
                    _graphTitleB = "Class Completed";
                    break;
                case "class":
                    _graphTitleA = "Average Score";
                    _graphTitleB = "Median Score";
                    break;
                case "student":
                    if (_additionalData == "") {
                        _graphTitleA = "Select a student below";
                    } else {
                        _graphTitleA = _additionalData + " average score";
                    }
                    _graphTitleB = "Class Score";
                    break;
                case "outcome":
                    break;
                cas
            }
            if (_type == "pie") {
                $("#graphBand").append(_graphVars.graphDivForPie);

                contentWidth = $(".charts").width();
                var colWidth = contentWidth;

                if (colWidth <= 420) {
                    var pieChartAX = $(".graphPointer").parent().position().left - 10;
                    $('#forPieChartA').css("left", pieChartAX + "px");
                    $('#forPieChartA').css("top", "25px");
                    $('#forPieChartB').css("left", pieChartAX + "px");
                    $('#forPieChartB').css("top", ($('#forPieChartA').position().top + 225) + "px");

                    _graphUtility.drawPieChartA(_leftPerc,_graphTitleA);
                    _graphUtility.drawPieChartB(_rightPerc,_graphTitleB);

                    $('#pieALabel').css("left", (pieChartAX + 55) + "px");
                    $('#pieBLabel').css("left", (pieChartAX + 68) + "px");
                    $('#pieALabel').css("top", ($('#pieALabel').position().top + 10) + "px");
                    $('#pieBLabel').css("top", ($('#pieBLabel').position().top + 20) + "px");
                    $('#pieBLabel').css("top", ($('#forPieChartB').position().top + 100) + "px");
                } else {
                    if (colWidth > 740)
                        colWidth = 740;

                    var pieWidth = 440 + ((colWidth - 440) / 2);
                    var pieChartAX = (colWidth / 2) - (pieWidth / 2);
                    var pieChartBX = pieChartAX + 260 + ((colWidth - 440) / 2) - 60;
                    $('#forPieChartA').css("left", pieChartAX + "px");
                    $('#forPieChartB').css("left", pieChartBX + "px");
                    
                    _graphUtility.drawPieChartA(_leftPerc, _graphTitleA);
                    _graphUtility.drawPieChartB(_rightPerc, _graphTitleB);

                    $('#pieALabel').css("left", (pieChartAX + 66) + "px");
                    $('#pieBLabel').css("left", (pieChartBX + 69) + "px");
                }
            } else if (_type == "bar") {
                $("#graphBand").append(_graphVars.graphDivForBar);
                _graphUtility.drawBarChart(_additionalData);

            }
        },
        drawBarChart: function (_data) {
            $('#forBarChart').highcharts({
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    labels: {
                        formatter: function () {
                            return '<span style="color:#007fa2;font-weight:bold">' + _data[this.value][0] + "</span>";
                        },
                        useHtml: true
                    },
                    lineWidth: 2,
                    lineColor: '#333333',
                    crosshair: true,
                    minorTickWidth: 0
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    },
                    max: 100,
                    lineWidth: 2,
                    lineColor: '#333333',
                    labels: {
                        formatter: function () {
                            return this.value + "%";
                        }
                    },
                    minorTickWidth: 0
                },
                legend: {
                    enabled: false
                },
                credits: {
                    enabled: false
                },
                tooltip: {
                    enabled: false
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        color: '#007fa2'
                    }
                },
                series: [{
                    name: 'Tokyo',
                    data: _data

                }]
            });
        },
        drawPieChartA: function (percScore, graphTitle) {
            //var percScore = (typeof QBPercScoring !== 'undefined') ? ((QBPercScoring.userSCore / QBPercScoring.totalScore) * 100).toFixed(0) : QLSimModule.GetTotalScore();
            percScore = Math.round(percScore);
            if (isNaN(percScore) || percScore == undefined || percScore == null) {
                percScore = 0;
            }

            var _startAngle = Math.abs(((Number(percScore) / 100) * 180) - 90 - 90);
            var _borderColor = "#1d7527";
            var _borderWidth = 1;

            if (percScore == 100) {

            } else if (percScore == 0) {
                _borderColor = "#d6f5da"
            } else {
                _borderWidth = 0;
            }
            var title = '<div style="width:260px;font-family:\'Open Sans\';color:#007fa2;font-size:14px;font-weight:bold;text-align:center;">' + graphTitle + ' <span style="font-family:\'Open Sans\';color:#333333;font-size:14px;font-weight:bold">' + percScore + '%</span></div>'
            if (graphTitle == "Select a student below") {
                title = '<div style="width:260px;font-family:\'Open Sans\';color:#007fa2;font-size:14px;font-weight:bold;text-align:center;">' + graphTitle + '</div>'
            }
            
            var containerA = document.getElementById('forPieChartA');
            
            runOnLoad(function(){
    	        new Highcharts.Chart({    	        		           
                chart: {
                	renderTo : containerA,
                	type: 'pie',
                    marginBottom: 0,
                    marginTop: 0,
                    marginLeft: 0,
                    marginRight: 0,
                    spacingLeft: 0,
                    spacingRight: 0,
                    spacingBottom: 0,
                    spacingTop: 0,
                    backgroundColor: null
                },
                title: {
                    text: title,
                    useHtml: true,
                    align: 'center',
                    y: 250,
                    floating: false
                },
                subtitle: {
                    text: ''
                },
                credits: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    pie: {
                        borderColor: _borderColor,
                        borderWidth: _borderWidth,
                        startAngle: _startAngle,
                        shadow: false,
                        size: 260,
                        center: ['50%', '50%']
                    }
                },
                tooltip: {
                    enabled: false
                },
                series: [{
                    name: '',
                    data: [{
                        y: Number(percScore),
                        color: '#1d7527'
                    }, {
                        y: Number(100 - percScore),
                        color: '#d6f5da'
                    }],
                    size: '80%',
                    innerSize: '75%',
                    dataLabels: {
                        connectorWidth: 0,
                        x: -180,
                        y: -20,
                        formatter: function () {
                            return null;
                        },
                        style: {
                            fontSize: 48,
                            fontWeight: 'normal',
                            fontFamily: 'arial',
                            color: '#007fa2'
                        }
                    }
                }]
    	        })
            });
            
            $("#graphBand").append(_graphVars.pieALabel);
            $("#pieALabel").html(percScore + "%")
        },
        drawPieChartB: function (percScore, graphTitle) {
           // var percScore = KnowdlTracking.getClassAverage();

            if (isNaN(percScore) || percScore == undefined || percScore == null) {
                percScore = 0;
            }

            var _startAngle = Math.abs(((Number(percScore) / 100) * 180) - 90 - 90);
            var _borderColor = "#1d7527";
            var _borderWidth = 1;

            if (percScore == 100) {

            } else if (percScore == 0) {
                _borderColor = "#d6f5da"
            } else {
                _borderWidth = 0;
            }
            
            var containerB = document.getElementById('forPieChartB');
            
            runOnLoad(function(){
    	        new Highcharts.Chart({    	        		           
                chart: {
                	renderTo : containerB,
                	type: 'pie',
                    marginBottom: 20,
                    marginTop: 20,
                    marginLeft: 0,
                    marginRight: 0,
                    spacingLeft: 0,
                    spacingRight: 0,
                    spacingBottom: 0,
                    spacingTop: 0,
                    backgroundColor: null
                },
                title: {
                    text: '<span style="font-family:\'Open Sans\';color:#007fa2;font-size:14px;font-weight:bold">' + graphTitle + ' <span style="font-family:\'Open Sans\';color:#333333;font-size:14px;font-weight:bold">' + percScore + '%</span>',
                    useHtml: true,
                    align: 'center',
                    y: 217,
                    floating: false
                },
                subtitle: {
                    text: ''
                },
                credits: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: ''
                    }
                },
                plotOptions: {
                    pie: {
                        borderColor: _borderColor,
                        borderWidth: _borderWidth,
                        startAngle: _startAngle,
                        shadow: false,
                        size: 200,
                        center: ['50%', '50%']
                    }
                },
                tooltip: {
                    enabled: false
                },
                series: [{
                    name: '',
                    data: [{
                        y: Number(percScore),
                        color: '#1d7527'
                    }, {
                        y: Number(100 - percScore),
                        color: '#d6f5da'
                    }],
                    size: '80%',
                    innerSize: '75%',
                    dataLabels: {
                        connectorWidth: 0,
                        x: -155,
                        y: -50,
                        formatter: function () {
                            return null;
                        },
                        style: {
                            fontSize: 42,
                            fontWeight: 'normal',
                            fontFamily: 'arial',
                            color: '#007fa2'
                        }
                    }
                }]
    	        })
            });
            $("#graphBand").append(_graphVars.pieBLabel);
            $("#pieBLabel").html(percScore + "%")
        }
    };
})();

$(".studentRow").live("click", function () {
    debugger;
    var _studentName = $(this).find("td:first").text().trim();;
    var stuId = $(this).attr("data-studentid");
    if ($(this).hasClass("studentDisplayed")) {
        $(this).removeClass("studentDisplayed");
        $("tr.studentDetailRow[data-studentid ='" + stuId + "']").hide();
        $("tr.studentDetailQuestionRow[data-studentid ='" + stuId + "']").removeClass("questionDisplayed")
        $("tr.studentDetailQuestionRow[data-studentid ='" + stuId + "']").hide();
    }
    else {
        $(".tblStudentDetails tr.questionDisplayed").removeClass("questionDisplayed");
        $(".tblStudentDetails tr.studentDisplayed").removeClass("studentDisplayed");
        $("tr.studentDetailRow").hide();
        $("tr.studentDetailQuestionRow").hide();

        $(this).addClass("studentDisplayed");
        $("tr.studentDetailRow[data-studentid ='" + stuId + "']").show();
        var pfirst = Number($(this).find("input[type='hidden']").val());
        var psecond = Number($("#hiddenClassReportAvgGrade").val());                
        _graphUtility.initialiseGraph(pfirst, psecond, "pie", "student", _studentName);
    }
});

$(".studentDetailRow").live("click", function () {
    debugger;
    var stuId = $(this).attr("data-studentid");
    var qsnId = $(this).attr("data-questionid");
    if ($(this).hasClass("questionDisplayed")) {
        $(this).removeClass("questionDisplayed");
        $("tr.studentDetailQuestionRow[data-studentid ='" + stuId + "'][data-questionid ='" + qsnId + "']").hide();
       
    }
    else {
        $(this).addClass("questionDisplayed");
        $("tr.studentDetailQuestionRow[data-studentid ='" + stuId + "'][data-questionid ='" + qsnId + "']").show();
    }
});
$("#ipStudentSearch").live("keyup", function () {
    //debugger;
    searchVal = $("#ipStudentSearch").val();

    if(searchVal == "")
    {
        $(".tblStudentDetails tr.studentRow,.tblStudentDetails tr.studentDetailQuestionRow,.tblStudentDetails tr.studentDetailRow").hide();
        $(".tblStudentDetails tr.questionDisplayed").removeClass("questionDisplayed");
        $(".tblStudentDetails tr.studentDisplayed").removeClass("studentDisplayed");
        $(".tblStudentDetails tr.studentRow").show();
    }
    else
    {
        $(".tblStudentDetails tr.questionDisplayed").removeClass("questionDisplayed");
        $(".tblStudentDetails tr.studentDisplayed").removeClass("studentDisplayed");
        searchVal = searchVal.toLowerCase();
        $(".tblStudentDetails tr").each(function () {
            if($(this).hasClass("studentRow"))
            {
                if($(this).text().toLowerCase().indexOf(searchVal)>=0)
                {
                    $(this).show();
                }
                else
                {
                    $(this).hide();
                }
            }
            else if ($(this).hasClass("studentDetailQuestionRow") || $(this).hasClass("studentDetailRow"))
            {
                $(this).hide();
            }
        })
    }
});

$(".student_review_link").live("click", function () {
    var sid = $(this).attr("sid");
    var attindex = $(this).attr("attno");
    var qlid = $(this).attr("qlid");
    var temp_problem_guid = gQLId;
	if (temp_problem_guid.indexOf('/business/it/') != -1){
	            temp_problem_guid = k_identifier_val
	}
	else{
	    temp_problem_guid = temp_problem_guid.replace('/armstrong', '').replace('/kotler', '').replace('/solomon', '')
	    temp_problem_guid = temp_problem_guid.replace('/ebert', '').replace('/bovee', '')
	    temp_problem_guid = temp_problem_guid.replace('/certo', '').replace('/robbins10 Simulation', '').replace('/robbins10', '').replace('/robbins14', '')
	temp_problem_guid = temp_problem_guid.replace('/david','').replace('/barringer','').replace('/dressler','').replace('/mariotti','').replace('/scarborough','')
	}
    temp_problem_guid = temp_problem_guid.replace('-', '_');
    var reviewurl = document.location.protocol + "/content/" + temp_problem_guid + "/#/" + sid + "/?att=" + attindex + "&mode=review";
    window.open(reviewurl, sid);
});

function ShowOutcomes()
{
    if ($(".tabContainer[rel='Outcomes']").find("table").length <= 0) {
        SetParameters();
        //var _data = { "QL_Id": gQLId, "LOC": gCourse_Id, "ASGN": gASGN };
        var servcUrl = "/knowdlanalytics/QLSimOutcomes/?Course_Id=" + gCourse_Id + "&ASGN=" + gASGN + "&QL_Id=" + gQLId;
        $.ajax({
            type: "GET",
            async: false,
            url: servcUrl,            
            success: function (result) {
            	debugger
                $("#analyticsResult .tabContainer[rel='Outcomes']").html(result);
                var graphdata = eval($("#hiddenOutcomeChartData").val());
                if (graphdata!=undefined && graphdata.length > 0) {
                    _graphUtility.initialiseGraph(0, 0, "bar", "outcomes", graphdata);
                }
            },
            error: function (error) {

            }
        });
    }
    else {
        var graphdata = eval($("#hiddenOutcomeChartData").val());
        if (graphdata != undefined && graphdata.length > 0) {
            _graphUtility.initialiseGraph(0, 0, "bar", "outcomes", graphdata);
        }
    }
}
