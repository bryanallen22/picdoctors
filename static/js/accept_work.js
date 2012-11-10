// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  var ApprovalView = Backbone.View.extend({
    initialize: function() {

    },

    events: {
      'click       .btn_accept_job': 'accept_job',
    },

    accept_job: function(){

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
        url:  '/accept_doctors_work/',
        data: json_data,
        success : function(data, textStatus) {
          console.log(data);
          console.log(textStatus);
          location.href = data.relocate;
        },

      });
    },

  });

  var av_el = $(".accept_view");
  var av = new ApprovalView({el:av_el});


});
