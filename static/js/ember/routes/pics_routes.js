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
