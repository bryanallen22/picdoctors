// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  var true_sync_func = Backbone.sync;
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
      xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
    };
    return true_sync_func( method, model, options);
  };

  var JobInfo = Backbone.Model.extend({
    // Default attributes for the Message Model
    defaults: function() {
      return {
        job_id               : -1,
        output_pic_count     : '',
        status               : 'Unknown',
        unread_message_count : 0,
        album                : -1,
        albumurl             : '',
        pic_thumbs           : [],
        dynamic_actions      : [],
        doctor_payout        : '',
        job_worth            : '',
        show_links           : false,
        tier                 : '',
      };
    },

    initialize : function() {
    },

    clear: function() {
      this.destroy();
    },

  });

  // A collection of JobInfo elements
  var JobList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: JobInfo,

    initialize: function() {
      this.container = null;
      this.bind('add', this.newJobRow, this);
      this.bind('reset', this.setup, this);
    },


    newJobRow: function (job_info){
      var view = new JobRowView( { model: job_info} );
      this.container.append(view.el);
    },

    setup: function(){
      var that = this;
      this.each( function(el) {
        that.newJobRow.call(that, el);
      });

    },

  });

  var JobRowView = Backbone.View.extend({

    className: 'row job_row fix_line_height',

    template:  '',

    initialize: function(){
      //this is set in the job.html page
      if(doc_page){
        this.template = _.template($('#doctor_row_template').html().trim());
      } else {
        this.template = _.template($('#user_row_template').html().trim());
      }
      this.model.bind('change',  this.render,       this);
      this.render();
    },

    events: {
      "click .dynamic_action_button" : "executeDynamicAction",
    },

    render: function(){
      // Compile the template using underscore

      this.$el.html(this.template(
        {
          job_id              : this.model.get('job_id'),
          output_pic_count    : this.model.get('output_pic_count'),
          status              : this.model.get('status'),
          unread_message_count: this.model.get('unread_message_count'),
          album               : this.model.get('album'),
          albumurl            : this.model.get('albumurl'),
          pic_thumbs          : this.model.get('pic_thumbs'),
          dynamic_actions     : this.model.get('dynamic_actions'),
          doctor_payout       : this.model.get('doctor_payout'),
          job_worth           : this.model.get('job_worth'),
          show_links          : this.model.get('show_links'),
          tier                : this.model.get('tier'),
        }
      ));
    },

    executeDynamicAction: function(event){
      var postback_url = $(event.target).attr('postback_url');
      var redir_val = $(event.target).attr('redir').toLowerCase();

      Logger.timestamp('execute dynamic action ' + postback_url); 

      if(redir_val == 'true') {
        location.href = postback_url;
        return;
      }

      var json_data = {
          "job_id" : this.model.get('job_id'),
        };
      var this_model = this.model;

      $.ajax({
        headers: {
          "X-CSRFToken":CSRF_TOKEN
        },
        type: 'POST',
        url:  postback_url ,
        data: json_data,
        success : function(data, textStatus) {
          dynamicReaction(data, this_model);
        },
        failure : function(jqXHR, textStatus, errorThrown) {
          //console.log(jqXHR);
          //console.log(textStatus);
          //console.log(errorThrown);
        }

      });

    },
  });

  function dynamicReaction(data, model) {
    var actions = data.actions;
    if(data.job_info!=null) {
      replace_job_row(data.job_info, model);
    }
    for (var i = 0; i < actions.length; i++) {
      var action = actions[i];
      switch(action.action)
      {
        case 'alert':
          var section = $("#alert_section");
          section.css('display','block');
          section.removeClass();
          section.addClass("alert alert_section");
          var alert_info = action.data;
          section.addClass("alert-" + alert_info.alert_class);
          $(".alert_words").text(alert_info.text);
          break;
        case 'reload':
          location.href = location.href;
          break;
        case 'redirect':
          location.href = action.data;
          break;
        case 'action_button':
          setup_action_buttons(action.data);
          break;
        case 'remove_job_row':
          remove_row_by_job_id(action.data);
          break;
        default:
          alert('Implementation failure for "' + action.action + '" with the data: "' + action.data + '"');
          break;
      }
    }
  }

  function replace_job_row(job_info, model) {
    var ji = job_info;

      model.set('job_id', ji.job_id);
      model.set('output_pic_count', ji.output_pic_count);
      model.set('status', ji.status);
      model.set('unread_message_count', ji.unread_message_count);
      model.set('album', ji.album);
      model.set('albumurl', ji.albumurl);
      model.set('pic_thumbs', ji.pic_thumbs);
      model.set('dynamic_actions', ji.dynamic_actions);
      model.set('doctor_payout', ji.doctor_payout);
      model.set('job_worth', ji.job_worth);
      $('.carousel').carousel('next');
      $('.carousel').carousel();
  }

  function remove_row_by_job_id(job_id) {
    var jr = $('.job_row');
    $('.job_row').each(function(){
      var job_id_div = $(this).find('.job_id');
      if(job_id_div.attr('job_id') == job_id){
        $(this).remove();
      }
    });

  }

  function setup_action_buttons(data){
        //Build the button template only once, that way you can click the buttons

        template = _.template( $('#redirect_buttons_template').html() );
        $(".redirect_row_buttons").html( this.template(
                {
                  href: data.href,
                  text: data.text,
                }
              ));

  }


  var job_list = new JobList();
  job_list.container = $("#jobs_rows");

  if(!$('.job_infos').length) return;

  var job_infos =  jQuery.parseJSON( $('.job_infos').html());
  job_list.reset(job_infos);
});
