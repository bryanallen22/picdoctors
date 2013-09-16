// In all reality you would put each route in its own file, but this is just for fun
Pd.ApplicationRoute = Ember.Route.extend({
  model: function(){
    // I like the idea of the application model being the user
    // the user is the center of our universe
    return this.get('store').find('user', -1);
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
    // the pics model is embedded in the group
    return this.modelFor('group').get('pics');
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

