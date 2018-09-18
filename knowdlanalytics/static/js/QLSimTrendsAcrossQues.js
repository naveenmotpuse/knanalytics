$("#selectedSim").live("change",function () {
    GetQuestionDetails();
});

$("#selectedLOC").live("change", function () {
    GetQuestionDetails();
});

function GetQuestionDetails() {
    var selectedSim = $("#selectedSim").val();
    var selectedLocation = $("#selectedLOC").val();   
    $.ajax({
        url: '/QLTrendsAcrossQuesDetails/',
        data: {
          'selsim': selectedSim, 'selloc' : selectedLocation
        },
        type: "GET",
        success: function (data) {
        	$("#questionDetails").html(data)
        }
      });
}

function UpdateGraph() {
 $(".graphDiv").each(function () {
	 	var container = this;
        var _ths = $(this);
        var graphVariable = _ths.closest("tr.questionRow").attr("data-forgraph");
        var arrGraphVariable = graphVariable.split("###");
        if(arrGraphVariable[0] == 0){
        	 return true;
        }
        var correct = arrGraphVariable[1] / arrGraphVariable[0] * 100;
        var incorrect = arrGraphVariable[2] / arrGraphVariable[0] * 100;
        var partial = arrGraphVariable[3] / arrGraphVariable[0] * 100;
        runOnLoad(function(){
	        new Highcharts.Chart({
	            chart: {
	            	renderTo : container,
	            	plotBackgroundColor: null,
	                plotBorderWidth: 0,//null,
	                plotShadow: false,
	                height: 75,
	                width: 75,
	                backgroundColor: null,
	            },
	            title: {
	                text: ''
	            },
	            tooltip: {
	                shared: false,
	            },
	            plotOptions: {
	                pie: {
	                    allowPointSelect: false,
	                    cursor: 'pointer',
	                    dataLabels: {
	                        enabled: false,
	                    }
	                }
	            },
	            credits: {
	                enabled: false
	            },
	            legend: {
	                enabled: false
	            },
	            series: [{
	                type: 'pie',
	                name: '',
	                data: [
	                    { y: correct, color: '#077c3c' },
	                    { y: incorrect, color: '#ef0b35' },
	                    { y: partial, color: '#efc12b' },
	
	                ],
	                enableMouseTracking: false,
	                states: {
	                    hover: {
	                        enabled: false
	                    }
	                }
	            }]
	        });
        });
    });
 
	$(".enlargedGraphDiv").each(function () {
		var container = this;
		var _ths = $(this);
        var graphVariable = _ths.closest("tr.questionDetailsRow").attr("data-forgraph");
        var arrGraphVariable = graphVariable.split("###");
        
        var correct = arrGraphVariable[1] / arrGraphVariable[0] * 100;
        var incorrect = arrGraphVariable[2] / arrGraphVariable[0] * 100;
        var partial = arrGraphVariable[3] / arrGraphVariable[0] * 100;
        
        runOnLoad(function(){
        	  new Highcharts.Chart({
                  chart: {
                  	 renderTo : container,
                  	  plotBackgroundColor: null,
                      plotBorderWidth: 0,//null,
                      plotShadow: false,
                      height: 300,
                      width: 310,
                      backgroundColor :null,
                  },
                  title: {
                      text: ''
                  },
                  tooltip: {
                      // pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                      formatter: function () {                   
                          return '<b>' + this.key + '</b> ';
                      }
                  },
                  plotOptions: {
                      pie: {
                    	  allowPointSelect: true,
                          cursor: 'pointer',
                          dataLabels: {
                              enabled: true,
                              formatter: function () {
                                  if (this.key == "correct") {
                                      return "<div style='color:#077c3c'>correct</div>"
                                  } else if (this.key == "incorrect") {
                                      return "<div style='color:#ef0b35'>incorrect</div>"
                                  } else if (this.key == "partial") {
                                      return "<div style='color:#efc12b '>partial</div>"
                                  } else {
                                      return ""
                                  }
                              },
                              useHTML: true
                          }
                      }
                  },
                  credits: {
                      enabled: false
                  },
                  legend: {
                      enabled: false
                  },
                  series: [{
                      type: 'pie',
                      name: '',               
                      data: [
                          { name: "correct", y: correct, color: '#077c3c' },
                          { name: "incorrect", y: incorrect, color: '#ef0b35' },
                          { name: "partial", y: partial, color: '#efc12b' },

                      ],
                      
                  }]
              });
        });
    });
}

$(".questionRow").live("click", function () {
    //debugger;
    var qsnId = $(this).attr("data-questionid");
    if ($(this).hasClass("optionsDisplayed")) {
        $(this).removeClass("optionsDisplayed");
        $("tr.questionDetailsRow[data-questionid ='" + qsnId + "']").hide();
    }
    else {
        $(this).addClass("optionsDisplayed");
        $("tr.questionDetailsRow[data-questionid ='" + qsnId + "']").show();
    }
})