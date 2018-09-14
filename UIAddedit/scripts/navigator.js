//This api will contain navigation logic and page load.
//It will also handle the question navigation if the page is having multiple questions.
var _Navigator = (function () {
    var _currentPageId = "";
    var _currentPageObject = {};
    var progressLevels = [1];
    var _NData = {
        "l1p1": {
            pageId: "l1p1",
            prevPageId: "",
            nextPageId: "l1p2",
            dataurl: "l1p1.htm",
            datalevel: 0,
            questions: [],
            isStartPage: true,
        },
        "l1p2": {
            pageId: "l1p2",
            prevPageId: "l1p1",
            nextPageId: "",
            dataurl: "l1p2.htm",
            datalevel: 1,
            questions: [],
        },
        "l1p3": {
            pageId: "l1p3",
            prevPageId: "l1p2",
            nextPageId: "",
            dataurl: "l1p3.htm",
            datalevel: 1,
            questions: [],
        }
    }
    var _StateData = {}

    function OnPageLoad() {
       // _TopSlider.OnLoad();
       // _CustomPage.OnPageLoad();
      // _Navigator.LoadDefaultQuestion();
    }
    return {
        Get: function () {
            return _NData;
        },
        Start: function () {
                this.LoadPage("l1p1");
        },
        LoadPage: function (pageId, jsonObj) {
            if (jsonObj == undefined) {
                jsonObj = {};
            }
            _currentPageId = pageId;
            this.UpdateProgressBar();
            _currentPageObject = _NData[_currentPageId]
            if (_currentPageObject.isStartPage != undefined && _currentPageObject.isStartPage) {
                $("#linkprevious").k_disable();
                $("#linknext").k_enable();
            }
            if(_currentPageObject.hasActivity !=undefined && _currentPageObject.hasActivity){
                $("#linknext").k_disable();
            }
            if (_currentPageObject.isLastPage != undefined && _currentPageObject.isLastPage) {
                $("#linknext").k_disable();
            }

            _currentPageObject.isVisited = true;

            var pageUrl = _Settings.dataRoot + _currentPageObject.dataurl + _Caching.GetUrlExtension();;
            if (_currentPageObject.isStartPage) {
                $(".main-content").load(pageUrl, function () {
                    OnPageLoad();
                    $("h1").focus();
                });
            } else {
                $(".main-content").fadeTo(250, 0.25, function () {
                    $(".main-content").load(pageUrl, function () {
                        $(this).fadeTo(600, 1)
                        OnPageLoad();
                        $("h2.pageheading").focus();
                    });
                })
            }
        },
        LoadDefaultQuestion: function () {
            if (_currentPageObject.questions.length > 0) {
                _questionId = 0;
                _currentPageObject.questions[0].isQuestionVisit = true;
                for (var i = 0; i < _currentPageObject.questions.length; i++) {
                    if (_currentPageObject.questions[i].isCurrent) {
                        _questionId = i;
                    }
                }
                //second parameter is to disable question effect.
                _Question.Load(_currentPageObject.questions[_questionId], {
                    disableEffect: true
                });
            }
        },
        Prev: function () {
            if (_currentPageObject.questions.length > 0) {
                if (_currentPageObject.questions[0].isCurrent) {
                    this.LoadPage(_currentPageObject.prevPageId);
                } else {
                    _Question.Prev();
                }
            } else {
                this.LoadPage(_currentPageObject.prevPageId);
            }
        },
        Next: function () {
            $("#linkprevious").k_enable();
            if(_currentPageObject.customNext!=undefined && !_currentPageObject.customNext.isComplete){
                var custFunction = new Function(_currentPageObject.customNext.jsFunction);
                custFunction();
            }
            else if (_currentPageObject.questions.length > 0) {
                var IsAllQCompleted = true;
                for (var i = 0; i < _currentPageObject.questions.length; i++) {
                    if (_currentPageObject.questions[i].isAnswered == undefined || !_currentPageObject.questions[i].isAnswered || _currentPageObject.questions[i].isQuestionVisit == undefined || !_currentPageObject.questions[i].isQuestionVisit) {
                        IsAllQCompleted = false;
                        break;
                    }
                }
                if (IsAllQCompleted) {
                    this.LoadPage(_currentPageObject.nextPageId);

                } else {
                    this.UpdateProgressBar();
                    _Question.Next();
                }
            } else {
                if (_currentPageObject.IsComplete == undefined || !_currentPageObject.IsComplete) {
                    this.CompletePage()
                }
                this.LoadPage(_currentPageObject.nextPageId);
            }
        },
        GetProgressData: function () {
            var progData = [];
       
            for (var p = 0; p < progressLevels.length; p++) {
                var visitpage = 0;
                for (var i in _NData) {
                    if (p == _NData[i].datalevel) {
                        if (_NData[i].questions.length > 0) {
                            for (var j = 0; j < _NData[i].questions.length; j++) {
                                if (_NData[i].questions[j].isAnswered) {
                                    visitpage++;
                                }
                            }
                        } else {
                            if (_NData[i].IsComplete) {
                                visitpage++;
                            }
                        }
                    }
                }
                progData.push(visitpage);
            }
            return progData;
        },
        UpdateProgressBar: function () {
            var progData = this.GetProgressData();
            for (var i = 0; i < progData.length; i++) {
                var lprog_pecent = (progData[i] / progressLevels[i] * 100).toFixed(2);
                $(".pgBgItem[data-level='" + i + "']").find(".pgBgItemFill").css("width", lprog_pecent + "%");
                if (lprog_pecent == 100) {
                    $(".pgBgItem[data-level='" + i + "']").addClass("pgBgItemComplete")
                }
            }
        },
        GetCurrentPage: function () {
            return _currentPageObject;
        },
        CompletePage: function (extendedJson) {
            _currentPageObject.IsComplete = true;
            _currentPageObject = $.extend(true, _currentPageObject, extendedJson)
            _StateData[_currentPageObject.pageId] = $.extend(true, {}, _currentPageObject);
        },
        GetTotalScore: function () {
            var ObtainPoint = 0;
            var totalPoints = 0;
            for (var i in _NData) {
                if (_NData[i].questions.length > 0) {
                    for (var j = 0; j < _NData[i].questions.length; j++) {
                        totalPoints = totalPoints + _QData[_NData[i].questions[j].Id].totalPoints;
                        if (_NData[i].questions[j].isAnswered != undefined && _NData[i].questions[j].isAnswered) {
                            ObtainPoint = ObtainPoint + (_NData[i].questions[j].points);
                        }
                    }
                }
            }
            var score = (ObtainPoint / totalPoints) * 100;
            return score.toFixed(0);
        },
        UpdateScore: function () {
            var percScore = this.GetTotalScore()
            $("#scoreInnrDiv").html(percScore + "%");
        },
    };
})();

$(document).on("click", "#linkprevious", function (event) {
    if ($(this).k_IsDisabled()) return;
    _Navigator.Prev();
});
$(document).on("click", "#linknext", function (event) {
    if ($(this).k_IsDisabled()) return;
    _Navigator.Next();
});