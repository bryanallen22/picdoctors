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
  setupController: function(){
    Ember.run.scheduleOnce('afterRender', function(){
      window.location.href = "/upload";
    });
  }
});
