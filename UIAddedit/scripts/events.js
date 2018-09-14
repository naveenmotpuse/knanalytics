
$(document).on("click", ".qheight", function (event) {
    $(".qheight").css({
        "background-color":"",
        "font-weight":"normal"
    })
    $(".question_icon").children("span").css({
        "background-color":"",
        "color": ""
    });
    $(this).css({
        "background-color":"#f1f1f1",
        "font-weight":"bold"
    });
    $(this).children(".question_icon").children("span").css({
        "background-color":"#003058",
        "color": "#F9FF00"
    });
});

$(document).on("click", ".infoIcon", function (event) {
    $("#infoIcon").html($(".intro-p").html());
    $("#infoIcon").slideToggle("slow", function () {

    });
});

$(document).on("click", ".collExpandIcon", function (event) {
     var self = $(this);
    if(self.text() == "+"){
        $(".AddQuestionRecord").slideDown("slow", function () {
            self.text('-');
         });
    }else{
        $(".AddQuestionRecord").slideUp("slow", function () {
            self.text('+');
         });
    }
});

var qdata=""
$(document).ready(function() {
    $('#inputTagBox').tagsInput({width:'auto'});
        $.ajax({
            type: "GET",
            url: 'scripts/data.txt',
            success: function (data) {
                qdata = JSON.parse(data)
                _QuestionCollection(qdata);
            },
            error: function (error) {
                _QuestionCollection(error);
            }
    });
});
$(document).on("click", "input[type='radio']", function (event) {
    var currentText = $(this).text();
   var q_id = $(this).closest("table").attr("qid")
    var opt_id =  $(this).closest("tr").attr("oid")
     for(var i=0; i < qdata.length; i++){
         if(qdata[i].QuestionId == q_id){
             if(opt_id.trim() != "" ){
                 for(var j=0; j < qdata[i].Options.length; j++){
                         if( qdata[i].Options[j].OptionId == opt_id){
                             qdata[i].Options[j].OptionText = currentText;
                         }
                 }
             }
             else{
                 qdata[i].QuestionText = currentText;
             }
         }
     }


 });
$(document).on("blur", "#editor", function (event) {
   var currentText = $(this).text();
  var q_id = $(this).closest("table").attr("qid")
   var opt_id =  $(this).closest("tr").attr("oid")
    for(var i=0; i < qdata.length; i++){
        if(qdata[i].QuestionId == q_id){
            if(opt_id.trim() != "" ){
                for(var j=0; j < qdata[i].Options.length; j++){
                        if( qdata[i].Options[j].OptionId == opt_id){
                            qdata[i].Options[j].OptionText = currentText;
                        }
                }
            }
            else{
                qdata[i].QuestionText = currentText;
            }
        }
    }


});



$(document).on("click", "#btnAddTag1", function (event) {
    var temp = $('#inputTagBox').val();
    var tempArr = temp != "" ? temp.split(",") : [];
    var aid = $(this).attr('aid');
    $('#inputTagBox').val('');
    for (var k = 0; k < tempArr.length; k++) {
        if ($('.temp01').tagExist(tempArr[k])) {
            //If tag already exists
        } else {
            $('.temp01').addTag(tempArr[k]);
        }
    }

    var $keywords = $(".temp01").siblings(".tagsinput").children(".tag");
    var tags = [];
    for (var i = 0; i < $keywords.length; i++) {
        tags.push($($keywords[i]).text().substring(0, $($keywords[i]).text().length - 1).trim());
    }

    $(".resourceTags[aid='" + aid + "']").attr("tags", tags.toString());
    var tempTags = encodeURIComponent(tags);
  //  fSaveTags(tempTags, aid);
});

function handlekeydown(e) {
    if (e.keyCode == 13) {
        $("#btnAddTag").click();
    }
}



function _QuestionCollection(_qdata){
      if(typeof(_qdata)=="object" && _qdata.length != 0){
           for(var i=0; i < _qdata.length; i++){
            var QuestionHtml ="<div class='OptionGroup'>" +
                              "<table qid='"+ _qdata[i].QuestionId +"'>" +
                                "<tbody>" +
                                 "<tr>" +
                                    "<td class='Qestion_no'><label><strong>Q" + _qdata[i].QuestionId + ".</strong>" +
                                            "</label>" +
                                        "</td>" +
                                        "<td class='QuestionText'>" +
                                            "<p contenteditable='true' id='editor'>"+ _qdata[i].QuestionText +"</p>" +
                                    "</td>" +
                                "</tr>";
               for(var j=0; j < _qdata[i].Options.length;j++){
                QuestionHtml += "<tr oid='"+ _qdata[i].Options[j].OptionId +"'>" +
                                    "<td>" +
                                        "<strong>Option"+ _qdata[i].Options[j].OptionId +"</strong>"+
                                    "</td>" +
                                    "<td class='tdoptiontext'>" +
                                        "<p contenteditable='true' id='editor'>" + _qdata[i].Options[j].OptionText+ "</p>" +
                                    "</td>" +
                                    "<td class='tdraioinput'>" +
                                        "<label>";
                                        if(_qdata[i].Options[j].IsCorrect == true){
                                            QuestionHtml +="<input type='radio' name='q" + i +"' value='option"+ j +"' checked> isCorrect";
                                        }else{
                                           QuestionHtml +="<input type='radio' name='q" + i +"' value='option"+ j +"'>";
                                        }

                QuestionHtml +=  "</label>" +
                                    "</td>" +
                                "</tr>";
               }
               QuestionHtml += "</tbody>" +
                            "</table>" +
                        "</div>" ;
               $(".AddQuestionRecord").append(QuestionHtml);
           }
      }else{
         $(".AddQuestionRecord").html("<h2>Question Not Found</h2>");
      }
}


