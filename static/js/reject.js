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
          location.href = data.relocate;
        },

      });

}


$(function(){

  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  var SwitchDoctorView = Backbone.View.extend({

    events: {
      'click': 'switch_doc',
    },

    switch_doc: function(){
      CallHome('/switch_doctor/', CSRF_TOKEN, this.$el.attr('job_id'));
    },
  });

  var RefundView = Backbone.View.extend({

    events: {
      'click': 'refund',
    },

    refund: function(){
      CallHome('/refund_user/', CSRF_TOKEN, this.$el.attr('job_id'));
    },

  });

  var IncreaseView = Backbone.View.extend({

    events: {
      'click' : 'increase',
    },

    increase: function(){
      CallHome('/increase_price_ep/', CSRF_TOKEN, this.$el.attr('job_id'));
    },

  });

  var sdv_el = $(".btn_switch");
  var sdv = new SwitchDoctorView({el:sdv_el});

  var ref_el = $(".btn_refund");
  var ref = new RefundView({el:ref_el});

  var inc_el = $(".btn_increase");
  var ref = new IncreaseView({el:inc_el});

});
