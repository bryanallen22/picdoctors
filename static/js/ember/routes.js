// In all reality you would put each route in its own file, but this is just for fun
Pd.ApplicationRoute = Ember.Route.extend({
  model: function(){
    this.pushMarkupStyles();
    // I like the idea of the application model being the user
    // the user is the center of our universe
    return this.get('store').find('user', -1);
  },

  pushMarkupStyles: function(){
    var store = this.get('store');
    Pd.MarkupStyle.FIXTURE.forEach(function(ms){
      store.push('markupStyle', ms);
    });
  }
});

Pd.SigninToPayRoute = Ember.Route.extend({

  setupController: function(controller, model){
    Ember.run.scheduleOnce('afterRender', function(){
      window.location.href = '/signin/?next=/set_price/';
    });
  }
});

Pd.AlbumsRoute = Ember.Route.extend({
  model: function(params){
    return []; // find all the albums
  }
});

Pd.AlbumRoute = Ember.Route.extend({
  model: function(params){
    return this.get('store').find('album', params.album_id);
  }
});

Pd.GroupsRoute = Ember.Route.extend({
  model: function(params){
    // the groups model is embedded in the album
    return this.modelFor('album').get('groups');
  }
});

Pd.GroupRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('groups').findProperty('id', params.group_id);
  }
});

Pd.PicsRoute = Ember.Route.extend({
  model: function(params){
    var store = this.get('store');
    // the pics model is embedded in the group
    var pics = this.modelFor('group').get('pics');
    pics.forEach(function(pic){
      var markups = pic.get('markups');
      for(var i = 0,len = markups.get('length'); i< len;i++){
        var markup = markups.objectAt(i);
        markup.set('markupStyle', store.find('markupStyle', i+1));
      }
    });
    return pics;
  }
});

Pd.PicsEditRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('pics');
  }
});

Pd.PicRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('pics').findProperty('id', params.pic_id);
  }
});

Pd.MarkupsRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('pic').get('markups');
  }
});

Pd.MarkupNavigationRoute = Ember.Route.extend({});

// there is a way to use a fixture adapter, but I need to find out how to use two different stores, one with
// a fixture adapter, the other with the rest adapter
Pd.MarkupStyle.FIXTURE = [
 {id: 1,   'name':'Blue',             'color':'#049cdb', 'border_style':'solid'},
 {id: 2,   'name':'Green',            'color':'#46a546', 'border_style':'solid'},
 {id: 3,   'name':'Red',              'color':'#9d261d', 'border_style':'solid'},
 {id: 4,   'name':'Yellow',           'color':'#ffc40d', 'border_style':'solid'},
 {id: 5,   'name':'Dark blue',        'color':'#0064cd', 'border_style':'solid'},
 {id: 6,   'name':'Orange',           'color':'#f89406', 'border_style':'solid'},
 {id: 7,   'name':'Pink',             'color':'#c3325f', 'border_style':'solid'},
 {id: 8,   'name':'Purple',           'color':'#7a43b6', 'border_style':'solid'},
 {id: 9,   'name':'Dotted blue',      'color':'#049cdb', 'border_style':'dotted'},
 {id: 10,  'name':'Dotted green',     'color':'#46a546', 'border_style':'dotted'},
 {id: 11,  'name':'Dotted red',       'color':'#9d261d', 'border_style':'dotted'},
 {id: 12,  'name':'Dotted yellow',    'color':'#ffc40d', 'border_style':'dotted'},
 {id: 13,  'name':'Dotted dark blue', 'color':'#0064cd', 'border_style':'dotted'},
 {id: 14,  'name':'Dotted orange',    'color':'#f89406', 'border_style':'dotted'},
 {id: 15,  'name':'Dotted pink',      'color':'#c3325f', 'border_style':'dotted'},
 {id: 16,  'name':'Dotted purple',    'color':'#7a43b6', 'border_style':'dotted'},
 {id: 17,  'name':'Dashed blue',      'color':'#049cdb', 'border_style':'dashed'},
 {id: 18,  'name':'Dashed green',     'color':'#46a546', 'border_style':'dashed'},
 {id: 19,  'name':'Dashed red',       'color':'#9d261d', 'border_style':'dashed'},
 {id: 20,  'name':'Dashed yellow',    'color':'#ffc40d', 'border_style':'dashed'},
 {id: 21,  'name':'Dashed dark blue', 'color':'#0064cd', 'border_style':'dashed'},
 {id: 22,  'name':'Dashed orange',    'color':'#f89406', 'border_style':'dashed'},
 {id: 23,  'name':'Dashed pink',      'color':'#c3325f', 'border_style':'dashed'},
 {id: 24,  'name':'Dashed purple',    'color':'#7a43b6', 'border_style':'dashed'}
];
