// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  // Our basic **Markup** model has 'left', 'top', 'width', 'height',
  // 'color', and 'description' attributes.
  var Markup = Backbone.Model.extend({

    // Default attributes for the todo item.
    defaults: function() {
      return {
        left:         0,
        top:          0,
        width:        0,
        height:       0,
        color:        '#ffffff',
        description:  '',
      };
    },
    
    initialize : function() {
      console.log("I'm making me a Markup model!");
      console.log(this);
    },

    clear: function() {
      this.destroy();
    },

    // TODO: get rid of this so the model is actually saved
    sync: function () { return false; },

  });

  // Markup Collection
  // ---------------

  // A collection of Markup elements
  var MarkupList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: Markup,

    // Url base
    //url: '/markups/',
    
    initialize: function() {
      this.container = null; // Will be set to our .pic_container element
      this.bind('add', this.addOne, this);
    },

    addOne: function(markup) {
      var view = new MarkupView({model: markup});
      this.container.append(view.render().el);
    }

  });

  // Todo Item View
  // --------------

  // The DOM element for a todo item...
  var MarkupView = Backbone.View.extend({

    //... is a div tag.
    tagName:  "div",

    className: "markup",

    // Cache the template function for a single item.
    template: _.template( $('#markup-template-styleattr').html().trim() ),

    // The DOM events specific to an item.
    events: {
      //"click .toggle"   : "toggleDone",
    },

    // The MarkupView listens for changes to its model, re-rendering.
    // Since there's a one-to-one correspondence between a **Markup** 
    // and a **MarkupView** in this app, we set a direct reference on 
    // the model for convenience.
    initialize: function() {
      console.log("And, in the morning, I'm making MarkupView(s)!");
      console.log(this);
      this.model.bind('change', this.render, this);
      this.model.bind('destroy', this.remove, this);
    },

    // Re-render the titles of the todo item.
    render: function() {
      this.$el.attr('style', this.template(this.model.toJSON()));
      //this.input = this.$('.edit');
      return this;
    },

  });

  // The Application
  // ---------------

  // Our overall **AppView** is the top-level piece of UI.
  var AppView = Backbone.View.extend({

    // Our template for the line of statistics at the bottom of the app.
    //statsTemplate: _.template($('#stats-template').html()),

    el: $("#markup_app"),

    // Delegated events for creating new items, and clearing completed ones.
    events: {
      //"keypress #new-todo":  "createOnEnter",
      "click .pic_container" : "createMarkup",
    },

    // At initialization we bind to the relevant events on the `Todos`
    // collection, when items are added or changed. Kick things off by
    // loading any preexisting todos that might be saved in *localStorage*.
    initialize: function() {

      console.log("AppView init");

      $(".pic_container").each( function(index) {
        // Create a MarkupList on each element
        var markup_list = new MarkupList;
        markup_list.container = $(this);
        $(this).data("markup_list", markup_list);

        //markup_list.bind('add', this.add
      });

      //this.input = this.$("#new-todo");
      //this.allCheckbox = this.$("#toggle-all")[0];

      //Todos.bind('add', this.addOne, this);
      //Todos.bind('reset', this.addAll, this);
      //Todos.bind('all', this.render, this);

      //this.footer = this.$('footer');
      //this.main = $('#main');

      //Todos.fetch();
    },

    // Re-rendering the App just means refreshing the statistics -- the rest
    // of the app doesn't change.
    render: function() {
      //var done = Todos.done().length;
      //var remaining = Todos.remaining().length;

      //if (Todos.length) {
      //  this.main.show();
      //  this.footer.show();
      //  //this.footer.html(this.statsTemplate({done: done, remaining: remaining}));
      //} else {
      //  this.main.hide();
      //  this.footer.hide();
      //}

      //this.allCheckbox.checked = !remaining;
    },

    // Add a single todo item to the list by creating a view for it, and
    // appending its element to the `<ul>`.
    //addOne: function(todo) {
    //  var view = new TodoView({model: todo});
    //  this.$("#todo-list").append(view.render().el);
    //},

    // Add all items in the **Todos** collection at once.
    //addAll: function() {
    //  Todos.each(this.addOne);
    //},

    // If you hit return in the main input field, create new **Todo** model,
    // persisting it to *localStorage*.
    //createOnEnter: function(e) {
    //  if (e.keyCode != 13) return;
    //  if (!this.input.val()) return;

    //  Todos.create({title: this.input.val()});
    //  this.input.val('');
    //},
    
    createMarkup: function(e) {
      console.log("AppView.createMarkup called! div making time at <"
                  + e.offsetX + ", " + event.offsetY + ">");
      console.log("e:::");
      console.log(e);
      var pic_container = $(e.target).parentsUntil(".pic_outer").last();
      var left = e.pageX - pic_container.offset().left;
      var top = e.pageY - pic_container.offset().top;

      /* e.currentTarget would be better, but apparently Redmond doesn't
       * like it. See here: http://www.quirksmode.org/js/events_order.html */
      pic_container.data("markup_list").create(
          {
            left:    left + 'px',
            top:     top + 'px',
            height:  '200px',
            width:   '200px',
            color:   '#46a546',
          }
      );
    },
  });

  // Finally, we kick things off by creating the **App**.
  var App = new AppView;

});
