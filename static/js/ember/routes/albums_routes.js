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
  redirect: function(){
    window.location.replace("/upload");
  }
});

Pd.AlbumPayRoute = Ember.Route.extend({
  redirect: function(){
    window.location.replace("/set_price");
  }
});

Pd.AlbumMarkupEditRoute = Ember.Route.extend({
  redirect: function(){
    var firstGroup = this.modelFor('album').get('groups.firstObject');
    var trans = this.transitionTo('pics.edit', firstGroup);
    trans.urlMethod = "replace";
  }
});

Pd.AlbumMarkupViewRoute = Ember.Route.extend({
  redirect: function(){
    var firstGroup = this.modelFor('album').get('groups.firstObject');
    var trans = this.transitionTo('pics.view', firstGroup);
    trans.urlMethod = "replace";
  }
});
