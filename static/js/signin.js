// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

    function postTo(url, obj, callback) {

      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: "POST",
        url: url,
        data: obj,
        success : callback,
      });

    }

  /* If the radio button says they've got an account, hide the confirm password
   * button. This shouldn't normally be necessary, but if they hit the back button
   * or something it can be checked. */
  if( $('input:radio[name=create_acct_radio]:checked').val() == 'have' ) {
      $("#confirm_password").hide();
      $("#nickname").hide();
      $("#nickname-info").hide();
      $("#tos").hide();
  }

  $('input:radio[name=create_acct_radio]').click( function() {
    var checked = $(this).val();
    if( checked == "create" ) {
      // Creating an account
      $("#confirm_password").show();
      $("#nickname").show();
      $("#nickname-info").show();
      $("#tos").show();
    }
    else if( checked == "have" ) {
      // They already have an account
      $("#confirm_password").hide();
      $("#nickname").hide();
      $("#nickname-info").hide();
      $("#tos").hide();
    }
  });

  var disableAutoNickName = false;

  $('#email').keyup(function(){
    if(!disableAutoNickName){
      $('#nickname').val(getValidNickName($(this).val()));
    }
  });

  $('#email').change(function(){
    console.log('email change');
    trimNick();
    checkValidNickName(true);
  });
  $('#nickname').change(function(){
    console.log('nickname change');
    trimNick();
    checkValidNickName(true);
  });

  $('#nickname').keyup(function(){
    console.log('nickname keyup');
    // disable auto nickname when they've entered the field and the length > 0
    disableAutoNickName = $(this).val().length > 0;
    checkValidNickName(false);
  });

  function getValidNickName(dirty){
    var atIdx = dirty.indexOf('@');
    if(atIdx>=0){
      dirty = dirty.substring(0, atIdx);
    }
    
    var valid_chars = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    var clean_str = '';
    for (var i = 0, len = dirty.length; i < len; i++) {
      if(valid_chars.indexOf(dirty[i])>=0){
        clean_str += dirty[i];   
      }
    }
    return clean_str.substring(0,32);
  };
  var validHtml= "The following rules apply for nicknames: <ul><li>Not blank</li><li>letters (a-z)</li><li>numbers (0-9)</li><li>underscores</li><li>no longer than 32 characters in length</li></ul>";

  function trimNick(){
    var el = $('#nickname');
    el.val(el.val().trim());
  }

  function checkValidNickName(postBack){
    console.log('check valid nickname');
    // We don't validate when we're signing in again
    var checked = $('input:radio[name=create_acct_radio]').val();
    if( checked == "have" ) {
      return;
    }

    var el = $('#nickname');
    var errorParent = $('#nickErrorParent');
    var errorDiv = $('#nickError');
    var btn = $("#btnsubmit");
    var nick = el.val();
    var cleanNick = getValidNickName(nick);

    nick = nick.trim();


    if(cleanNick!=nick || nick.length == 0){
      console.log('nick already failed test');
      errorDiv.html("Your nickname is invalid<br/>" + validHtml);
      errorParent.show();
      btn.attr('disabled', 'disabled');
      return;
    }
      if($.inArray(nick, used)>=0){
        errorDiv.html("That nickname appears to already be taken, please try another.");
        errorParent.show();
        btn.attr('disabled', 'disabled');
        return;
      }

    if(postBack){
      console.log('post nick name');
        var obj = {
          'nickname'    : nick,
        };

        btn.attr('disabled', 'disabled');

        postTo('/check_unique_nickname/', obj, function(data) {
          uniqueNameResponse(data, obj);
        });
    }
    else
    {
        errorParent.hide();
        btn.removeAttr('disabled');
    }
  };
  var used = [];
  
  function uniqueNameResponse(data, obj){
    var errorParent = $('#nickErrorParent');
    var errorDiv = $('#nickError');
    var btn = $("#btnsubmit");

    errorParent.hide();

    if(data.success){
      console.log("nickname looks good!");
      btn.removeAttr('disabled');
      
    } else {
      used.push(obj.nickname);
      btn.attr('disabled', 'disabled');
      checkValidNickName(false);
    }

  };


});
