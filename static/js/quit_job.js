// Load the application once the DOM is ready, using `jQuery.ready`:


function CallHome(url, csrf, job_id){
      var json_data = JSON.stringify(
        {
          "job_id" : job_id,
        }
      );
      
      $.ajax({
        headers: {
          "X-CSRFToken":csrf
        },
        type: 'POST',
        url:  url,
        data: json_data,
        success : function(data, textStatus) {
          console.log(data);
          console.log(textStatus);
          location.href = data.relocate;
        },

      });

}


$(function(){

  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  var QuitJobView = Backbone.View.extend({

    events: {
      'click                      ': 'quit_job',
    },

    quit_job: function(){
      CallHome('/quit_job_endpoint/', CSRF_TOKEN, this.$el.attr('job_id'));
    },

  });

  var NevermindView = Backbone.View.extend({

    events: {
      'click                      ': 'nevermind',
    },

    nevermind: function(){
      window.history.back();
    },
  });

  var sdv_el = $(".btn_quit");
  var sdv = new QuitJobView({el:sdv_el});

  var nvm_el = $(".btn_nevermind");
  var nvm = new NevermindView({el:nvm_el});


});
