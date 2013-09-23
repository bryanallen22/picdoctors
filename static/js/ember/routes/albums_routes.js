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

Pd.AlbumUploadRoute = Ember.Route.extend({
  afterModel: function(){
    window.location.replace("/upload");
  }
});

Pd.AlbumPayRoute = Ember.Route.extend({
  afterModel: function(){
    window.location.replace("/set_price");
  }
});

Pd.AlbumMarkupEditRoute = Ember.Route.extend({
  afterModel: function(){
    var firstGroup = this.modelFor('album').get('groups.firstObject');
    // replace this route in the history
    this.replaceWith('pics.edit', firstGroup);
  }
});

Pd.AlbumMarkupViewRoute = Ember.Route.extend({
  afterModel: function(){
    var firstGroup = this.modelFor('album').get('groups.firstObject');
    // replace this route in the history
    this.replaceWith('pics.view', firstGroup);
  }
});
