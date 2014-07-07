// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  if( $("#signin").length > 0 ) {
    var checkNickName = true;

    /* If the radio button says they've got an account, hide the confirm password
     * button. This shouldn't normally be necessary, but if they hit the back button
     * or something it can be checked. */
    if( $('input:radio[name=create_acct_radio]:checked').val() == 'have' ) {
      haveChecked();
    }

    $('input:radio[name=create_acct_radio]').click( function() {
      var checked = $(this).val();
      if( checked == "create" ) {
        // Creating an account
        checkNickName = true;
        $("#confirm_password").show();
        $("#nickname").show();
        $("#nickname-info").show();
        $("#tos").show();
      }
      else if( checked == "have" ) {
        haveChecked();
      }
    });

    function haveChecked(){
      // They already have an account
      checkNickName = false;
      $("#confirm_password").hide();
      $("#nickname").hide();
      $("#nickname-info").hide();
      $('#nickErrorParent').hide();
      $("#tos").hide();
      $("#btnsubmit").removeAttr('disabled');
    }

    var disableAutoNickName = false;

    $('#email').keyup(function(){
      if(!checkNickName) return;

      if(!disableAutoNickName){
        $('#nickname').val(getValidNickName($(this).val()));
      }
    });

    $('#nickname').keyup(function(){
      if(!checkNickName) return;

      Logger.timestamp('nickname keyup', 5); 
      // disable auto nickname when they've entered the field and the length > 0
      disableAutoNickName = $(this).val().length > 0;
      checkValidNickName(false);
    });

    var onChange = function(){
      if(!checkNickName) return;

      Logger.timestamp('email/nickname change', 5); 
      trimNick();
      checkValidNickName(true);
    };

    $('#email, #nickname').change(onChange);

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
      Logger.timestamp('check valid nickname', 5); 
      // We don't validate when we're signing in again
      var el = $('#nickname'),
          errorParent = $('#nickErrorParent'),
          errorDiv = $('#nickError'),
          btn = $("#btnsubmit"),
          nick = el.val(),
          cleanNick = getValidNickName(nick),
          checked = $('input:radio[name=create_acct_radio]').val();

      if( checked == "have" ) {
        return;
      }

      if(cleanNick!=nick || nick.length == 0){
        Logger.timestamp('nick already failed test', 5); 
        errorDiv.html("Your nickname is invalid<br/>" + validHtml);
        errorParent.show();
        btn.attr('disabled', 'disabled');
        return;
      }

      if($.inArray(nick, used) >= 0){
        errorDiv.html("That nickname appears to already be taken, please try another.");
        errorParent.show();
        btn.attr('disabled', 'disabled');
        return;
      }

      if(postBack){
        Logger.timestamp('post nick name', 5); 
        var obj = {
          'nickname'    : nick,
        };

        btn.attr('disabled', 'disabled');

        postTo('/check_unique_nickname/', obj, function(data) {
          uniqueNameResponse(data, obj);
        });
      } else {
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
        Logger.timestamp('nick name is good', 5); 
        btn.removeAttr('disabled');

      } else {
        used.push(obj.nickname);
        btn.attr('disabled', 'disabled');
        checkValidNickName(false);
      }

    };
  }

});
