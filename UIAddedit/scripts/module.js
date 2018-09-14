jQuery.fn.extend({
    k_enable: function() {
        return this.removeClass('disabled').attr("aria-disabled","false").removeAttr("disabled");
    },
    k_disable: function() {
        return this.addClass('disabled').attr("aria-disabled","true").attr("disabled", "disabled");
    },
    k_IsDisabled: function(){
       if( this.hasClass('disabled')){return true;}else{return false;}
    }
  });


$(document).ready(function () {
    _Navigator.Start();    
    $("h1:first").focus();

    if(_Settings.enableCache)
    {
        _Caching.InitAssetsCaching();
        _Caching.InitPageCaching();
    }
});