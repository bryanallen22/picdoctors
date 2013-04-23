
$(function(){
  if( $('#acceptwork_app').length > 0 ) {
    $(".rating").rating({showCancel: false, startValue: null});  

    $("#accept_job").submit( function() {
      $("#rating_val").val($(".rating").val());

      var checked = $("input[name='allow_publicly']:checked");
      if(checked.length > 0) {
        $("#allow_publicly").hide();
        $("#btn_accept").attr('disabled', 'disabled');
        return true;
      }
      else {
        $("#allow_publicly").show();
        return false;
      }
    });
  }
});

