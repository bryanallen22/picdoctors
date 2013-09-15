window.Pd = Pd = Ember.Application.create({
  rootElement: '#ember-container',
  LOG_TRANSITIONS: true
});

Pd.RestAdapter = DS.RESTAdapter.extend({
  namespace: 'api'
});

Pd.Store = DS.Store.extend({
  adapter: 'Pd.RestAdapter'
});


Pd.Router.map(function(){
  this.resource('albums' , { path: 'albums'}, function(){
    this.resource('album', { path: ':album_id'}, function(){
      this.resource('groups', {path: 'groups'}, function(){
        this.resource('group', {path: ':group_id'}, function(){
          this.resource('pics', {path: 'pics'}, function(){
            this.route('edit');
            this.resource('pic', {path: ':pic_id'}, function(){
              this.resource('markups', {path: 'markups'}, function(){
              });
            });
          });
        });
      });
    });
  });
});

