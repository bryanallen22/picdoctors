function get_rating(){
  $("#rating_val").val($(".rating").val());
  return true;
}

$(function(){
  $(".rating").rating({showCancel: false, startValue: null});  
});

