$(document).ready(function () {
//	$(".NiceSelectBoxStyle").niceSelect();
	//ShowQLSimAnalyticsDetails();
});
	
function ShowQLSimAnalyticsDetails() {
	QLId = $("#selectedSim").val();
    LOC = $("#selectedLOC").val();
    ASGN = $("#selectedASGN").val();
    
	var _data = { "QL_Id": QLId, "ASGN": LOC, "Course_Id": ASGN };
	$.ajax({
      type: "GET",
      async: false,
      url: '/QLSimAnalyticsDetails',
      data: _data,
      success: function (result) {
          $("#analyticsReport").html(result);
      },
      error: function (error) {

      }
  });
}
$("#selectedSim").live("change", function () {
    if($("#selectedSim").val()!="") {
    	debugger
        var servcUrl = "/GetAssignmentsString";
        $.ajax({
            type: "GET",
            async: false,
            url: servcUrl,
            data: { "QL_Id": $("#selectedSim").val()},
            success: function (result) {
                $("#selectedASGN").empty().append(result);
            },
            error: function (error) {

            }
        });
    }
});

$("#selectedLOC").live("change", function () {
    if ($("#selectedLOC").val() != "") {
    	debugger
    	var servcUrl = "/GetLocQLString";
        $.ajax({
            type: "GET",
            async: false,
            url: servcUrl,
            data: { "LOC": $("#selectedLOC").val() },
            success: function (result) {
                $("#selectedSim").empty().append(result);
            },
            error: function (error) {

            }
        });
    }
});

$("#btnGo").live("click", function () {
    $("#analyticsResult .tabContainer").empty();
    $(".asgnTitle").html(document.getElementById("selectedASGN").options[document.getElementById("selectedASGN").selectedIndex].text);
	QLId = $("#selectedSim").val();
    LOC = $("#selectedLOC").val();
    ASGN = $("#selectedASGN").val();
    $(".ql .tabs a.reporttab[rel='Overview']").click();
});
