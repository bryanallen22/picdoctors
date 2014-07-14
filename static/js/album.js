$(function(){

  if( $('#album_app').length > 0 ) {
    var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

    var RemoteControl = Backbone.View.extend({
      events: {
   //     'click       .before_button': 'before_click',
   //     'click       .after_button':  'after_click',
      },

      initialize: function() {
      },

    });

    var CombinationView = Backbone.View.extend({
      initialize: function() {
        var rc_el = this.$el.find('.remote_control');
        this.remote_control = new RemoteControl({el: rc_el});

        this.before_after = this.$el.find('.picbeforeafter');
        this.before_after.qbeforeafter({defaultgap:50, leftgap:0, rightgap:0, caption: true, reveal: 0.5});
      },

    });

    $(".combination").each( function(){
      var cb = new CombinationView({el:this});
    });

    var ApprovalView = Backbone.View.extend({
      initialize: function() {

      },

      events: {
        'click       .btn_approve_all': 'approve_all',
      },

      approve_all: function(){
        /* Disable button */
        $('.btn_approve_all').attr("disabled", "disabled");
        var json_data = JSON.stringify(
          {
            "job_id" : this.$el.attr('job_id'),
          }
        );

        $.ajax({
          headers: {
            "X-CSRFToken":CSRF_TOKEN
          },
          type: 'POST',
          url:  '/approve_album/',
          data: json_data,
          success : function(data, textStatus) {
            /* Enable button - probably unnecessary, but useful if redirect fails */
            $('.btn_approve_all').removeAttr("disabled");
            location.href = data.redirect;
          }
        });
      },
    });

    var av_el = $(".album_control");
    var av = new ApprovalView({el:av_el});

    var downloadURL = function downloadURL(url) {
      var hiddenIFrameID = 'hiddenDownloader',
          iframe = document.getElementById(hiddenIFrameID);
      if (iframe === null) {
          iframe = document.createElement('iframe');
          iframe.id = hiddenIFrameID;
          iframe.style.display = 'none';
          document.body.appendChild(iframe);
      }
      iframe.src = url;
    };

    $("#download_original").click( function(e) {
      e.preventDefault();
      var url = $(this).attr('href');
      //console.log("downloading " + url);
      downloadURL(url);
    });
  }
});

/* These are global because they are in the 'onclick' events. Probably fine, but annoying anyway.*/
window.replace_fancy_user_pic = function(el, id){
  el = $(el);
  var par = $('#' + id);
  var child = par.find('.ba-mask');

  child.css('background-image', 'url(' + el.attr('data-pic') + ')');

}

window.replace_normal_user_pic = function(el, id){
  el = $(el);
  var rep = $('#' + id);
  rep.css('background-image', 'url(' + el.attr('data-pic') + ')');

}

window.make_album_shareable = function(el, id){
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');

  var json_data = JSON.stringify( { } );

  $.ajax({
     headers: {
       "X-CSRFToken":CSRF_TOKEN
     },
     type: 'GET',
     url:  '/make_album_shareable/' + id,
     data: json_data,
     success : function(data, textStatus) {
       $(".gallery_not_public").hide();
       $("#gallery_now_public").html("The album is now public and shareable!");
     }

  });
}
