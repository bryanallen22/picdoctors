Pd.AlbumsController = Ember.ArrayController.extend({});
Pd.AlbumController = Ember.ObjectController.extend({
  needs : ['application'],

  user: function(){
    return this.get('controllers.application.model');
  }.property('controllers.application.model'),

  isAlbumOwner: function(){
    return this.get('user.id') == this.get('owner');
  }.property('user', 'owner'),

  isAlbumDoctor: function(){
    return this.get('user.id') == this.get('doctor');
  }.property('user', 'doctor'),

});
