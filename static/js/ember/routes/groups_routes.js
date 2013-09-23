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

Pd.GroupNavigationRoute = Ember.Route.extend({});
