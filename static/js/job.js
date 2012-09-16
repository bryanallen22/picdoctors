// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){
  var Job = Backbone.Model.extend({

    // Default attributes for the todo item.
    defaults: function() {
      return {
        // These match directly to server side logic
        id:                     0, 
        user_batch:             0,
        doctor_batch:           0,
        price:                  0,
        // I'm not sure if I want to include this in the client side logic...
        price_too_low_count:    0,
        // TODO
        // doctor:              0,
        job_status:             '',
      };
    },
    
    initialize : function() {
    },

    clear: function() {
      this.destroy();
    },

  });

  var true_sync_func = Backbone.sync;
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
      xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
    };
    return true_sync_func( method, model, options);
  };

  // Job Collection
  // ---------------

  // A collection of Markup elements
  var JobList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: Job,

    // Url base
    url: '/job_handler/',

    initialize: function() {
//      this.container = null; 
    },

  });

  // The Application
  // ---------------

  // Our overall **AppView** is the top-level piece of UI.
  var AppView = Backbone.View.extend({

    el: $("#job_app"),


    initialize: function() {

    /*  //console.log("AppView init");

      $(".markup_outer").each( function() {
        // Create a MarkupList on each element
        var markup_list = new MarkupList;
        // Give markup_list a pointer to his container element,
        // and give the container element a pointer to his markuplist.
        markup_list.container = $(this).find(".markup_pic_container");
        $(this).data("markup_list", markup_list);

        var general_instructions = $(this).find(".desc").val() ;
        var pic_model = new Pic( {uuid: markup_list.container.attr('uuid'),
                                  general_instructions: general_instructions } );
        
        var instruction = $(this).find(".instruction");

        new GeneralInstructionView( { el : instruction, model: pic_model } );
        markup_list.reset( jQuery.parseJSON( $(this).find('.preloaded_markups').html() ) );
      });
*/
    },

    render: function() {
        console.log('render job view');
    },

  });

  // Finally, we kick things off by creating the **App**.
  var Jobs = new JobView;

});
