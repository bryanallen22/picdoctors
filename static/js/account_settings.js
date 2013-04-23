// This script gets loaded on both the account settings page for both users
// and doctors.

$(function(){

  if( $('#account_settings').length > 0 ) {
    /*
     * This dealio will let you put #some_tab in the url and it'll automatically
     * select that tab when the page loads
     */
    if ( window.location.hash ) {
      // They put the id in the url, and it gets clicked.
      // Used to preselect tabs settings
      $( window.location.hash ).click();
    }

    /*
     * Bank account stuff
     */
    /* uri comes directly from template */
    balanced.init(marketplace_uri);

    var $form = $('#bank-account-form');

    function submitToken(bank_account_uri) {
      var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

      var obj = { "bank_account_uri" : bank_account_uri };

      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: "POST",
        url: '/create_bank_account/',
        data: obj,
        success : function(data) {
          if ( data.success ) {
            // reload the page (on this tab)
            console.log('reloaaaad!');
            // TODO - use window.location.reload if we are already here?
            window.location = window.location.pathname + "#bank_tab";
            window.location.reload()
          }
          else {
            // Silently fail to do anything if we are unable to delete.
            // REVISIT
          }
        },
      });

    }

    function callbackHandler(response) {
      switch (response.status) {
        case 201:
          // WOO HOO!
          // response.data.uri == uri of the card or bank account resource
          submitToken(response.data.uri);
          break;

        case 400:
          // missing field - check response.error for details
          //break;
        case 402:
          // we couldn't authorize the buyer's credit card
          // check response.error for details
          //break;
        case 404:
          // your marketplace URI is incorrect
          //break;
        case 500:
          // Balanced did something bad, please retry the request
          //break;
        default:
          $('#error_bankaccount').show();
          break;
      }
    }

    var createAcct = function() {
      var bankAccountData = {
         "name": $form.find(".ba-name").val(),
         "account_number": $form.find(".ba-an").val(),
         "routing_number": $form.find(".ba-rn").val(),
         "type": $form.find("select option:selected").val(),
      }

      if( !balanced.bankAccount.validateRoutingNumber( bankAccountData.routing_number) )
      {
        $("#routing-error").show();
        return;
      }

      if( !balanced.bankAccount.validate({
             'routing_number' : bankAccountData.routing_number,
             'account_number' : bankAccountData.account_number,
             'name'           : bankAccountData.name }))
      {
        $('#error_bankaccount').show();
      }

      balanced.bankAccount.create(bankAccountData, callbackHandler);
    }

    $form.find("button:submit").click( function(e) {
      e.preventDefault();
      $('#error_bankaccount').hide();
      createAcct();
    });

    $(".delete_bank_account").click( function() {
      var bank_account_uri = $(this).parent().find(".uri").text();

      var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

      var obj = { "bank_account_uri" : bank_account_uri };

      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: "POST",
        url: '/delete_bank_account/',
        data: obj,
        success : function(data) {
          if ( data.success ) {
            // reload the page (on this tab)
            console.log('reloaaaad!');
            // TODO - use window.location.reload if we are already here?
            window.location = window.location.pathname + "#bank_tab";
            window.location.reload()
          }
          else {
            // Silently fail to do anything if we are unable to delete.
            // REVISIT
          }
        },
      });
    });

    /*
     * Merchant Info stuff
     */

    $('input:radio[name=merchant_type]').click( function() {
      var checked = $(this).val();
      if( checked == "person" ) {
        // Individual person
        $(".business_field").hide();
      }
      else if( checked == "business" ) {
        // They already have an account
        $(".business_field").show();
      }
    });

    $('.phone_number').keypress( function(e) {
      // Stop the normal entry of the key (we want to format it first)
      e.preventDefault();

      // append this keypress
      var val = $(this).val() + String.fromCharCode(e.which);

      // strip out all non-numerics
      val = val.replace(/[^0-9]/g, '');

      // strip long distance leading 1, if it's there
      if(val[0] == '1') {
        val = val.slice(1);
      }

      var p1 = val.slice(0,3);
      var p2 = val.slice(3,6);
      var p3 = val.slice(6,10);

      if(p1.length > 0) {
        var fmt_val = "(" + p1;
        if(p1.length == 3) {
          fmt_val += ") " + p2;
          if(p2.length == 3) {
            fmt_val += "-" + p3;
          }
        }
        $(this).val(fmt_val);
      }

    });

    /*
     * Password/email stuff
     */
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

    $("#password-form").find("button:submit").click( function(e) {
      e.preventDefault();

      // Disable the button
      var $button = $(this);
      $button.attr("disabled", "disabled");

      // if there is already an alert showing, hide it
      $(".password_alert").hide();

      var obj = {
        'old_password' :      $('input[name="old_password"]').val(),
        'new_password' :      $('input[name="new_password"]').val(),
        'confirm_password' :  $('input[name="confirm_password"]').val(),
      };

      postTo('/change_password/', obj, function(data) {
        // enable the button again
        $button.removeAttr("disabled");

        if ( data.success ) {
          $("#password-success").show();
        }
        else if ( data.bad_oldpassword ) {
          $("#password-oldbad").show();
        }
        else if ( data.nomatch ) {
          $("#password-nomatch").show();
        }
      });
    });


    $("#formRoles").find(".onoffswitch-checkbox").click( function() {

      var on = $(this).is(':checked');

      obj = {
        'role'    : this.id,
        'state'   : on,
      };

      postTo('/update_roles/', obj, function(data) {

        if ( data.success ) {
          if (data.redirect) {
              window.location.reload(data.redirect);
          }
        } else {
          alert('There was an error!');
        }
        
      });
    });

    var true_sync_func = Backbone.sync;
    Backbone.sync = function(method, model, options){
      options.beforeSend = function(xhr){
        xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
      };
      return true_sync_func( method, model, options);
    };

  /***************************************************************
   * Notification Settings
   * ************************************************************/
  // Load the application once the DOM is ready, using `jQuery.ready`:

    var NotificationInfo = Backbone.Model.extend({
      defaults: function() {
        return {
          type                 : '',
          description          : '',
          enabled              : false,
        };
      },
      
      initialize : function() {
      },

      clear: function() {
        this.destroy();
      },

    });

    // A collection of JobInfo elements
    var NotificationList = Backbone.Collection.extend({

      // Reference to this collection's model.
      model: NotificationInfo,

      url: '/notification_handler/',

      initialize: function() {
        this.container = null; 
        this.bind('reset', this.setup, this);
      },


      newNotificationRow: function (n_info){
        var view = new NotificationView( { model: n_info} );
        this.container.append(view.el);
      },

      setup: function(){
        var that = this;
        this.each( function(el) {
          that.newNotificationRow.call(that, el);
        });

      },

    });

    var NotificationView = Backbone.View.extend({
      
      className: 'row',

      template:  '',

      initialize: function(){
        //this is set in the job.html page
        this.template = _.template($('#notification_template').html().trim());
        this.model.bind('change',  this.render,       this);
        this.render();
      },

      events: {
        "click       .onoffemailswitch-checkbox" : "changeNotification",
      },

      render: function(){
        // Compile the template using underscore
        
        this.$el.html(this.template(
          {
            type                : this.model.get('type'),
            description         : this.model.get('description'),
            enabled             : this.model.get('enabled'),
          }
        ));
      },

      changeNotification: function(something){
        var checked = this.$el.find('.onoffemailswitch-checkbox').is(':checked');
        this.model.save({'enabled' : checked }, { wait : true});
      },


    });


    var ProfileView = Backbone.View.extend({
      
      el: $('#profile-form'),

      template:  '',

      // Delegated events for creating new items, and clearing completed ones.
      events: {
        //"keypress #new-todo":  "createOnEnter",
        "blur      #new_nickname"         : "check_unique_nickname",
        "click     #profile_submit"       : "profile_submit",
      },

      initialize: function(){
        //this is set in the job.html page
      //  this.model.bind('change',  this.render,       this);
      },

      hide_messages: function(){
         this.$el.find("#profile_error").hide();
         this.$el.find("#profile_success").hide();
      },

      handle_response: function(data){
          if (  data.success ) {
            this.$el.find("#profile_success").show();
            this.$el.find("#profile_success_text").text( data.text );
          } else {
            this.$el.find("#profile_error").show();
            this.$el.find("#profile_error_text").text( data.text );
          }

      },

      check_unique_nickname: function(){
        this.hide_messages();

        var obj = {
          'nickname'    : this.$el.find("#new_nickname").val(),
        };

        var this_view = this;

        postTo('/check_unique_nickname/', obj, function(data) {
          this_view.handle_response(data);
        });

      },

      profile_submit: function(){
        this.hide_messages();

        var obj = {
          'nickname'    : this.$el.find("#new_nickname").val(),
          'email'    : this.$el.find("#new_email").val(),
        };

        var button = this.$el.find("#profile_submit");
        var this_view = this;

        // disable button
        button.attr("disabled", "disabled");

        postTo('/change_profile_settings/', obj, function(data) {
          this_view.handle_response(data);
          // enable the button again
          button.removeAttr("disabled");

          });
      },

    });

    var pf = new ProfileView;

    var list = new NotificationList();
    list.container = $("#notifications-form");
    var notification_infos =  jQuery.parseJSON( $('.notification_infos').html());
    list.reset(notification_infos);
  }
});

